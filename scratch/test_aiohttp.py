import asyncio
import aiohttp
import os

async def main():
    key = os.environ.get("RIOT_API_KEY")
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/kanaki/kaan?api_key={key}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(response.status)
            print(await response.text())

asyncio.run(main())
