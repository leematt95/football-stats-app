#!/usr/bin/env python3
# import_players.py

import os
import sys
import asyncio
import logging
import aiohttp

from sqlalchemy import (
    create_engine, Table, Column, Integer, String, MetaData,
    TIMESTAMP, func, exc as sa_exc
)
from sqlalchemy.dialects.postgresql import insert
from understat import Understat

# ── Configuration & Logging ────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("import_players")

# Environment‑backed config with sensible defaults
DB_URL = os.getenv(
    "postgresql://localhost/football_db"
)
LEAGUE = os.getenv("LEAGUE", "epl")
SEASON = os.getenv("SEASON", "2025")

# Validate SEASON is an integer
try:
    SEASON = str(int(SEASON))
except ValueError:
    logger.error(f"Invalid SEASON value: {SEASON!r}. Must be an integer string.")
    sys.exit(1)

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
    logger.info(f"DB URL: {DB_URL}")
    logger.info(f"League: {LEAGUE}, Season: {SEASON}")
    asyncio.run(fetch_and_store())


# ── Documentation ───────────────────────────────────────────────────────────
# Import players from Understat and store in PostgreSQL
# Usage: Set environment variables DATABASE_URL, LEAGUE, SEASON as needed
# Ensure the database is running and accessible
# Run this script to fetch and store player data
# Example: python import_players.py
# This script uses asyncio and aiohttp for asynchronous HTTP requests
# It uses SQLAlchemy for database interactions
# The Understat library is used to fetch player data from the Understat API
# The script handles upserts to avoid duplicate entries in the database
# It logs the process and any errors encountered during execution
# Make sure to install the required packages: understat, aiohttp, sqlalchemy, psycopg2-binary
# Example: pip install understat aiohttp sqlalchemy psycopg2-binary
# The script is designed to be run as a standalone application
# It can be integrated into a larger application or run independently
# Ensure the database schema matches the expected structure for the players table
# The script can be modified to handle additional fields or different leagues/seasons
# It can also be extended to handle more complex data processing or validation
# The logging configuration can be adjusted as needed for different environments
# The script is designed to be efficient and handle large datasets
# It uses bulk operations to minimize database interactions
# The script can be scheduled to run periodically to keep the player data up-to-date
# It can also be integrated into a web application to provide real-time player data
# The script is a good starting point for building a football stats application
# It can be extended with additional features such as player statistics, match results, etc.
# The script can be tested with different leagues and seasons to ensure flexibility
# It can also be adapted for different data sources or APIs as needed
# The script is designed to be modular and easy to maintain
# It can be refactored into smaller functions or classes for better organization    