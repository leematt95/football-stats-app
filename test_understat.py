import asyncio
from understat import Understat
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        players = await understat.get_league_players("EPL", 2023)
        for p in players[:3]:
            print({
                "Name": p["player_name"],
                "Team": p["team_title"],
                "Goals": p["goals"],
                "Assists": p["assists"],
                "Minutes": p["time"]
            })

asyncio.run(main())
