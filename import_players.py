#!/usr/bin/env python3
# import_players.py

import os
import sys
import asyncio
import logging
import aiohttp
from dotenv import load_dotenv
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, TIMESTAMP, func, exc as sa_exc
from sqlalchemy.dialects.postgresql import insert
from understat import Understat

# ── Load Environment Variables ─────────────────────────────────────────────

load_dotenv()

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:securepass123@localhost:5432/football_db"
)
LEAGUE = os.getenv("LEAGUE", "epl")
SEASON = os.getenv("SEASON", "2025")

# Validate SEASON is an integer
try:
    SEASON = str(int(SEASON))
except ValueError:
    logger.error(f"Invalid SEASON value: {SEASON!r}. Must be an integer string.")
    sys.exit(1)

# ── Configuration & Logging ────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("import_players")
logger.info(f"Connecting to database: {DB_URL}")
logger.info(f"League: {LEAGUE}, Season: {SEASON}")

# ── Database Schema Setup ──────────────────────────────────────────────────

engine = create_engine(DB_URL, echo=False)
metadata = MetaData()

players = Table(
    "players",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column("age", Integer),
    Column("position", String),
    Column("team", String),
    Column("goals", Integer),
    Column("assists", Integer),
    Column("nationality", String),
    Column("last_updated", TIMESTAMP, server_default=func.now(), nullable=False),
)

# Create table if it doesn't already exist
metadata.create_all(engine)

# ── Helpers ────────────────────────────────────────────────────────────────

def to_int(val):
    """Safely convert val to int, defaulting to 0 on failure."""
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0

# ── Main Import Logic ──────────────────────────────────────────────────────

async def fetch_and_store():
    """Fetch player stats from Understat and upsert into Postgres."""
    try:
        # 1. Create an HTTP session for Understat
        async with aiohttp.ClientSession() as session:
            understat = Understat(session)
            logger.info(f"Fetching {LEAGUE.upper()} players for season {SEASON}…")
            data = await understat.get_league_players(LEAGUE, SEASON)

        if not data:
            logger.warning("No player data returned; exiting.")
            return

        # 2. Prepare rows, skipping malformed entries
        rows = []
        for p in data:
            name = p.get("player_name")
            team = p.get("team_title")
            if not name or not team:
                logger.warning(f"Skipping invalid entry: {p}")
                continue

            rows.append({
                "name":        name,
                "age":         to_int(p.get("age")),
                "position":    p.get("position"),
                "team":        team,
                "goals":       to_int(p.get("goals")),
                "assists":     to_int(p.get("assists")),
                "nationality": p.get("nationality"),
            })

        if not rows:
            logger.warning("No valid player rows to insert; exiting.")
            return

        # 3. Perform upsert in a single transaction
        with engine.begin() as conn:
            stmt = insert(players).values(rows)
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=["name"],
                set_={
                    **{c.name: getattr(stmt.excluded, c.name)
                       for c in players.columns
                       if c.name not in ("id", "last_updated")},
                    "last_updated": func.now()
                }
            )
            conn.execute(upsert_stmt)

        logger.info(f"Successfully imported/updated {len(rows)} players.")

    except aiohttp.ClientError as e:
        logger.error(f"HTTP error while fetching data: {e}")
    except sa_exc.SQLAlchemyError as e:
        logger.error(f"Database error during upsert: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")

# ── Entrypoint ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Starting import_players.py")
    asyncio.run(fetch_and_store())