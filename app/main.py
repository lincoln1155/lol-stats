import os
import asyncio
import aiohttp
import redis.asyncio as redis
import json

from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from pydantic import BaseModel
from google import genai

from app.utils import riot_get
from app.models import Match
from app.database import Base, get_db, engine
from app.chat import format_matches_for_prompt, generate_response, load_item_names

MAX_CONCURRENT_REQUESTS = 10
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

load_dotenv(".env")
RIOT_KEY = os.environ.get("RIOT_API_KEY")
REDIS_URL = os.environ.get("REDIS_URL")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session = aiohttp.ClientSession()
    app.state.redis = redis.from_url(REDIS_URL, decode_responses=True)
    app.state.genai = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await load_item_names()

    yield
    await app.state.session.close()
    await app.state.redis.close()

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/search/{region}/{riot_id}")
async def search_page(region: str, riot_id: str):
    return FileResponse(str(STATIC_DIR / "index.html"))

async def request_puuid_by_summoner_id(session, riot_id, region, key):
    riot_id = riot_id.split("-")
    if len(riot_id) != 2:
        raise HTTPException(status_code=400, detail="Invalid format, use Name-TAG")
    
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_id[0]}/{riot_id[1]}?api_key={key}"
    

    data = await riot_get(session, url)
    return data.get('puuid')
    
async def get_matchid_by_puuid(session, puuid, region, key):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={key}"
    
    return await riot_get(session, url)
    
async def get_match_data_by_id(session, match_id, region, key):

    async with semaphore:
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={key}"
        
        return await riot_get(session, url)
    
async def search_matches_db(match_ids: list, db: AsyncSession):
    """Bulk lookup — returns a dict of {match_id: data} for matches already in the DB."""
    query = select(Match).where(Match.match_id.in_(match_ids))
    result = await db.execute(query)

    return {m.match_id: m.data for m in result.scalars().all()}

def process_match_data(match_data, puuid):
    participants = match_data['info']['participants']
    for player in participants:
        if player['puuid'] == puuid:
            stats = {
                'username': f"{player['riotIdGameName']}#{player['riotIdTagline']}",
                'role': player['individualPosition'],
                'champion': player['championName'],
                'kda': f"{player['kills']}/{player['deaths']}/{player['assists']}",
                'gold': player['goldEarned'],
                'cs': player['totalMinionsKilled'] + player['neutralMinionsKilled'],
                'win': player['win']
            }
            return stats
    return None

class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None

@app.get("/matches/{region}/{riot_id}")
async def search_matches(region: str, riot_id: str, db: AsyncSession = Depends(get_db)):
    session = app.state.session

    cache_key = f"view:{riot_id.lower()}"
    cached = await app.state.redis.get(cache_key)
    if cached:
        print("in redis")
        return {"source": "cache", "data": json.loads(cached)}

    puuid = await request_puuid_by_summoner_id(session, riot_id, region, RIOT_KEY)

    match_ids = await get_matchid_by_puuid(session, puuid, region, RIOT_KEY)

    # Bulk lookup: find which matches are already persisted
    db_matches = await search_matches_db(match_ids, db)

    # Fetch missing matches concurrently (semaphore limits to 10 at a time)
    missing_ids = [m_id for m_id in match_ids if m_id not in db_matches]

    if missing_ids:
        tasks = [get_match_data_by_id(session, m_id, region, RIOT_KEY) for m_id in missing_ids]
        fetched = await asyncio.gather(*tasks, return_exceptions=True)

        for m_id, match_data in zip(missing_ids, fetched):
            if isinstance(match_data, Exception):
                continue
            db_matches[m_id] = match_data
            db.add(Match(match_id=m_id, summoner_puuid=puuid, data=match_data))

    await db.commit()

    # Process stats preserving original match order
    results = []
    for m_id in match_ids:
        match_data = db_matches.get(m_id)
        if match_data:
            stats = process_match_data(match_data, puuid)
            results.append(stats)

    await app.state.redis.setex(cache_key, 300, json.dumps(results))

    return {
        "source": "api/db",
        "data": results
    }


async def get_full_match_data(region: str, riot_id: str, db: AsyncSession):
    """Fetch full match JSON data for a player. Reuses existing logic."""
    session = app.state.session
    puuid = await request_puuid_by_summoner_id(session, riot_id, region, RIOT_KEY)
    match_ids = await get_matchid_by_puuid(session, puuid, region, RIOT_KEY)

    db_matches = await search_matches_db(match_ids, db)

    missing_ids = [m_id for m_id in match_ids if m_id not in db_matches]
    if missing_ids:
        tasks = [get_match_data_by_id(session, m_id, region, RIOT_KEY) for m_id in missing_ids]
        fetched = await asyncio.gather(*tasks, return_exceptions=True)
        for m_id, match_data in zip(missing_ids, fetched):
            if isinstance(match_data, Exception):
                continue
            db_matches[m_id] = match_data
            db.add(Match(match_id=m_id, summoner_puuid=puuid, data=match_data))
        await db.commit()

    # Return full match data in order + puuid
    matches = [db_matches[m_id] for m_id in match_ids if m_id in db_matches]
    return matches, puuid


@app.post("/chat/{region}/{riot_id}")
async def chat(region: str, riot_id: str, body: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not app.state.genai:
        raise HTTPException(status_code=503, detail="AI chat is not configured. Set GEMINI_API_KEY in .env")

    matches, puuid = await get_full_match_data(region, riot_id, db)

    if not matches:
        raise HTTPException(status_code=404, detail="No match data found for this player")

    context = format_matches_for_prompt(matches, puuid)
    response = await generate_response(
        client=app.state.genai,
        question=body.message,
        matches_context=context,
        chat_history=body.history,
    )

    return {"response": response}