import os
import asyncio
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import riot_get
from app.models import Match

MAX_CONCURRENT_REQUESTS = 10
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
RIOT_KEY = os.environ.get("RIOT_API_KEY")

async def request_puuid_by_summoner_id(session, riot_id, region, key):
    riot_id_parts = riot_id.split("-")
    if len(riot_id_parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid format, use Name-TAG")
    
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_id_parts[0]}/{riot_id_parts[1]}?api_key={key}"
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

async def get_full_match_data(session, region: str, riot_id: str, db: AsyncSession):
    """Fetch full match JSON data for a player. Reuses existing logic."""
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
