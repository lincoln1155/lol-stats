import asyncio
import aiohttp
import os

async def main():
    key = os.environ.get("RIOT_API_KEY")
    puuid = "cOeM5dVthWK3cKULi9iYJY48c87n_TOFPaMAx1zSIT0fRj6bdRwZRSY_JS26uOcqpYqVqJ-VfhK3og"
    
    url = f"https://br1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={key}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            print("League by PUUID:", r.status, await r.text())

asyncio.run(main())
