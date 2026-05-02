import asyncio
import aiohttp
import os

async def main():
    key = os.environ.get("RIOT_API_KEY")
    puuid = "cOeM5dVthWK3cKULi9iYJY48c87n_TOFPaMAx1zSIT0fRj6bdRwZRSY_JS26uOcqpYqVqJ-VfhK3og"
    
    url2 = f"https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={key}"
    url3 = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10&api_key={key}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url2) as r2:
            print("Summoner:", r2.status, await r2.text())
        async with session.get(url3) as r3:
            print("Matches:", r3.status, await r3.text())

asyncio.run(main())
