import json
import asyncio
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Match
from app.services.riot_service import (
    request_puuid_by_summoner_id,
    get_matchid_by_puuid,
    search_matches_db,
    get_match_data_by_id,
    process_match_data,
    RIOT_KEY
)

router = APIRouter()

@router.get("/matches/{region}/{riot_id}")
async def search_matches(request: Request, region: str, riot_id: str, db: AsyncSession = Depends(get_db)):
    session = request.app.state.session

    cache_key = f"view:{riot_id.lower()}"
    cached = await request.app.state.redis.get(cache_key)
    if cached:
        return {"source": "cache", "data": json.loads(cached)}

    puuid = await request_puuid_by_summoner_id(session, riot_id, region, RIOT_KEY)
    match_ids = await get_matchid_by_puuid(session, puuid, region, RIOT_KEY)

    # Bulk lookup: find which matches are already persisted
    db_matches = await search_matches_db(match_ids, db)

    # Fetch missing matches concurrently
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
            if stats:
                results.append(stats)

    await request.app.state.redis.setex(cache_key, 300, json.dumps(results))

    return {
        "source": "api/db",
        "data": results
    }
