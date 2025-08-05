#!/usr/bin/env python3
# import_players.py

import asyncio
import logging
import os
import sys
from typing import Dict, List, Optional, Union

import aiohttp
from dotenv import load_dotenv
from sqlalchemy import (
    TIMESTAMP,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)
from sqlalchemy import exc as sa_exc
from sqlalchemy import (
    func,
)
from sqlalchemy.dialects.postgresql import insert
from understat import Understat  # type: ignore[import]

# ── Load Environment Variables ─────────────────────────────────────────────

load_dotenv()

# ── Build Database URL ─────────────────────────────────────────────────────
# Prefer full DATABASE_URL if provided, else compose from parts exactly once
_database_url: Optional[str] = os.getenv("DATABASE_URL")
if _database_url:
    db_url: str = _database_url
else:
    db_user: str = os.getenv("POSTGRES_USER", "admin")
    db_pass: str = os.getenv("POSTGRES_PASSWORD", "securepass123")
    db_name: str = os.getenv("POSTGRES_DB", "football_db")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "5432")
    db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# ── Config & Logging ───────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("import_players")

# Validate critical variables
if not db_url:
    logger.error("Database URL could not be constructed.")
    sys.exit(1)

league: str = os.getenv("LEAGUE", "epl")
season_env: str = os.getenv("SEASON", "2025")

# Validate SEASON is integer
try:
    season: str = str(int(season_env))
except ValueError:
    logger.error(f"Invalid SEASON value: {season_env!r}. Must be integer.")
    sys.exit(1)

logger.info(f"Connecting to database: {db_url}")
logger.info(f"League: {league}, Season: {season}")

# ── Database Schema Setup ──────────────────────────────────────────────────

engine = create_engine(db_url, echo=False)
metadata = MetaData()

players = Table(
    "players",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column("position", String),
    Column("team", String),
    Column("goals", Integer),
    Column("assists", Integer),
    Column("games", Integer),
    Column("minutes", Integer),
    Column("xg", String),  # Expected goals (decimal)
    Column("xa", String),  # Expected assists (decimal)
    Column("shots", Integer),
    Column("key_passes", Integer),
    Column("yellow_cards", Integer),
    Column("red_cards", Integer),
    Column("last_updated", TIMESTAMP, server_default=func.now(), nullable=False),
)
# Create table if not exists
metadata.create_all(engine)

# ── Helpers ────────────────────────────────────────────────────────────────


def to_int(val: Union[str, int, None]) -> int:
    """Convert val to int, raising ValueError for invalid data."""
    if val is None:
        raise ValueError("Cannot convert None to integer")
    return int(val)


# ── Main Import Logic ──────────────────────────────────────────────────────


async def fetch_and_store() -> None:
    try:
        async with aiohttp.ClientSession() as session:
            understat = Understat(session)
            logger.info(f"Fetching {league.upper()} players for season {season}…")
            data = await understat.get_league_players(league, season)

        if not data:
            logger.warning("No player data returned; exiting.")
            return

        rows: List[Dict[str, Union[str, int]]] = []
        for p in data:
            name = p.get("player_name")
            team = p.get("team_title")
            if not name or not team:
                logger.warning(f"Skipping invalid entry: {p}")
                continue
            rows.append(
                {
                    "name": name,
                    "position": p.get("position"),
                    "team": team,
                    "goals": to_int(p.get("goals")),
                    "assists": to_int(p.get("assists")),
                    "games": to_int(p.get("games")),
                    "minutes": to_int(p.get("time")),  # 'time' field is minutes played
                    "xg": p.get("xG"),  # Keep as string for precision
                    "xa": p.get("xA"),  # Keep as string for precision
                    "shots": to_int(p.get("shots")),
                    "key_passes": to_int(p.get("key_passes")),
                    "yellow_cards": to_int(p.get("yellow_cards")),
                    "red_cards": to_int(p.get("red_cards")),
                }
            )

        if not rows:
            logger.warning("No valid player rows to insert; exiting.")
            return

        with engine.begin() as conn:
            stmt = insert(players).values(rows)
            upsert = stmt.on_conflict_do_update(
                index_elements=["name"],
                set_={
                    **{
                        c.name: getattr(stmt.excluded, c.name)
                        for c in players.columns
                        if c.name not in ("id", "last_updated")
                    },
                    "last_updated": func.now(),
                },
            )
            conn.execute(upsert)

        logger.info(f"Successfully imported/updated {len(rows)} players.")

    except aiohttp.ClientError as e:
        logger.error(f"HTTP error while fetching data: {e}")
    except sa_exc.SQLAlchemyError as e:
        logger.error(f"Database error during upsert: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")


if __name__ == "__main__":
    logger.info("Starting import_players.py")
    asyncio.run(fetch_and_store())
    logger.info("Finished import_players.py")
# ── End of import_players.py ───────────────────────────────────────────────
