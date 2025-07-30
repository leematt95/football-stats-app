#!/usr/bin/env python3
"""
Debug script to inspect raw Understat API data structure
"""
import asyncio
import json
import logging
import os
from typing import Any, Dict

import aiohttp
from dotenv import load_dotenv
from understat import Understat

load_dotenv()

async def debug_understat_data() -> None:
    """Fetch and inspect raw data from Understat API"""
    league = os.getenv("LEAGUE", "epl")
    season = os.getenv("SEASON", "2025")
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        async with aiohttp.ClientSession() as session:
            understat = Understat(session)
            logger.info(f"Fetching {league.upper()} players for season {season}...")
            data = await understat.get_league_players(league, season)
            
        if not data:
            logger.warning("No data returned")
            return
            
        # Show first player's complete data structure
        logger.info(f"Total players fetched: {len(data)}")
        if data:
            first_player = data[0]
            logger.info("First player data structure:")
            print(json.dumps(first_player, indent=2, default=str))
            
            # Show available keys
            logger.info(f"Available keys: {list(first_player.keys())}")
            
            # Sample a few players to check data variety
            logger.info("\nSample of key fields from first 5 players:")
            for i, player in enumerate(data[:5]):
                print(f"Player {i+1}: {player.get('player_name', 'NO_NAME')}")
                print(f"  Age: {player.get('age', 'MISSING')}")
                print(f"  Nationality: {player.get('nationality', 'MISSING')}")
                print(f"  Team: {player.get('team_title', 'MISSING')}")
                print(f"  Goals: {player.get('goals', 'MISSING')}")
                print(f"  Assists: {player.get('assists', 'MISSING')}")
                print()
                
    except Exception as e:
        logger.exception(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_understat_data())
