import asyncio
from understat import Understat
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        players = await understat.get_league_players("EPL", 2023)
        for p in players[:3]:
            print({
                "name": p["player_name"],
                "team": p["team_title"],
                "goals": p["goals"],
                "assists": p["assists"],
                "minutes": p["time"]
            })

asyncio.run(main())
