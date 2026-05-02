import asyncio
import aiohttp
import os

async def main():
    key = os.environ.get("RIOT_API_KEY")
    puuid = "cOeM5dVthWK3cKULi9iYJY48c87n_TOFPaMAx1zSIT0fRj6bdRwZRSY_JS26uOcqpYqVqJ-VfhK3og"
    
    url2 = f"https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={key}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url2) as r2:
            summoner_info = await r2.json()
            summ_id = summoner_info.get('id')
            url4 = f"https://br1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summ_id}?api_key={key}"
            async with session.get(url4) as r4:
                print("League:", r4.status, await r4.text())

asyncio.run(main())
