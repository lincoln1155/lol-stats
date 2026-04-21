import os
import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from contextlib import asynccontextmanager

MAX_CONCURRENT_REQUESTS = 10
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

load_dotenv(".env")
RIOT_KEY = os.environ.get("RIOT_API_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session = aiohttp.ClientSession()
    
    yield
    await app.state.session.close()

app = FastAPI(lifespan=lifespan)

async def request_puuid_by_summoner_id(session, riot_id, region, key):
    riot_id = riot_id.split("-")
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_id[0]}/{riot_id[1]}?api_key={key}"
    
    async with session.get(url) as response:
        data = await response.json()
        return data['puuid']
    
async def get_matchid_by_puuid(session, puuid, region, key):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={key}"
    
    async with session.get(url) as response:
        return await response.json()
    
async def get_match_data_by_id(session, match_id, region, key):

    async with semaphore:
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={key}"
        async with session.get(url) as response:
            if response.status == 429:
                print('Rate limit!')
            
            return await response.json()
        
def process_match_data(match_data, puuid):
    participants = match_data['info']['participants']
    for player in participants:
        if player['puuid'] == puuid:
            stats = {
                'username': f'{player['riotIdGameName']}#{player['riotIdTagline']}',
                'role': player['individualPosition'],
                'champion': player['championName'],
                'kda': f"{player['kills']}/{player['deaths']}/{player['assists']}",
                'gold': player['goldEarned'],
                'cs': player['totalMinionsKilled'],
                'win': player['win']
            }
            return stats
    return None

@app.get("/matches/{region}/{riot_id}")
async def search_matches(region: str, riot_id: str):
    session = app.state.session

    puuid = await request_puuid_by_summoner_id(session, riot_id, region, RIOT_KEY)
    if not puuid:
        raise HTTPException(status_code=404, detail="Player not found")
    match_ids = await get_matchid_by_puuid(session, puuid, region, RIOT_KEY)

    tasks = [get_match_data_by_id(session, m_id, region, RIOT_KEY) for m_id in match_ids]

    all_matches = await asyncio.gather(*tasks, return_exceptions=True)

    print(f"Last 20 matches: for {riot_id[0]}#{riot_id[1]}")

    results = []
    for match in all_matches:
        stats = process_match_data(match, puuid)
        if stats:
            results.append(stats)
    
    return {
        "summoner": f"{riot_id}",
        "matches": results
    }