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
    
    routing_region = "americas"
    if region in ["euw1", "eun1", "tr1", "ru"]: routing_region = "europe"
    elif region in ["kr", "jp1"]: routing_region = "asia"
    elif region in ["oc1", "ph2", "sg2", "th2", "tw2", "vn2"]: routing_region = "sea"
    
    url = f"https://{routing_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_id_parts[0]}/{riot_id_parts[1]}?api_key={key}"
    data = await riot_get(session, url)
    return data.get('puuid')
    
async def get_matchid_by_puuid(session, puuid, region, key):
    # Map routing region (e.g., br1) to regional routing for match-v5 (e.g., americas)
    # Riot uses regional endpoints for match history: americas, asia, europe, sea.
    # We will assume Americas for br1/na1, Europe for euw1, etc.
    routing_region = "americas"
    if region in ["euw1", "eun1", "tr1", "ru"]: routing_region = "europe"
    elif region in ["kr", "jp1"]: routing_region = "asia"
    elif region in ["oc1", "ph2", "sg2", "th2", "tw2", "vn2"]: routing_region = "sea"
    
    url = f"https://{routing_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10&api_key={key}"
    return await riot_get(session, url)

async def get_summoner_info(session, puuid, region, key):
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={key}"
    return await riot_get(session, url)

async def get_league_info(session, puuid, region, key):
    url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={key}"
    try:
        return await riot_get(session, url)
    except HTTPException as e:
        if e.status_code == 403:
            print(f"Warning: League API returned 403 Forbidden. Falling back to unranked. URL: {url}")
            return []
        raise e

async def get_match_data_by_id(session, match_id, region, key):
    routing_region = "americas"
    if region in ["euw1", "eun1", "tr1", "ru"]: routing_region = "europe"
    elif region in ["kr", "jp1"]: routing_region = "asia"
    elif region in ["oc1", "ph2", "sg2", "th2", "tw2", "vn2"]: routing_region = "sea"
    
    async with semaphore:
        url = f"https://{routing_region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={key}"
        return await riot_get(session, url)
    
async def search_matches_db(match_ids: list, db: AsyncSession):
    """Bulk lookup — returns a dict of {match_id: data} for matches already in the DB."""
    query = select(Match).where(Match.match_id.in_(match_ids))
    result = await db.execute(query)
    return {m.match_id: m.data for m in result.scalars().all()}

def parse_match_detailed(match_data, puuid):
    info = match_data.get('info', {})
    participants = info.get('participants', [])
    
    target_player = next((p for p in participants if p.get('puuid') == puuid), None)
    if not target_player:
        return None

    # Parse Teams for the right side column
    team_100 = []
    team_200 = []
    for p in participants:
        player_obj = {
            "championName": p.get("championName"),
            "summonerName": p.get("riotIdGameName") or p.get("summonerName", ""),
            "tagLine": p.get("riotIdTagline", ""),
            "puuid": p.get("puuid")
        }
        if p.get("teamId") == 100:
            team_100.append(player_obj)
        else:
            team_200.append(player_obj)

    # Queue type mapping (simplified)
    queue_id = info.get("queueId", 0)
    queue_map = {420: "Ranked Solo", 440: "Ranked Flex", 400: "Draft Pick", 430: "Blind Pick", 450: "ARAM", 1700: "Arena"}
    queue_name = queue_map.get(queue_id, "Normal Game")

    return {
        "matchId": match_data.get("metadata", {}).get("matchId"),
        "gameCreation": info.get("gameCreation", 0),
        "gameDuration": info.get("gameDuration", 0),
        "queueName": queue_name,
        "win": target_player.get("win", False),
        
        "championName": target_player.get("championName"),
        "kills": target_player.get("kills", 0),
        "deaths": target_player.get("deaths", 0),
        "assists": target_player.get("assists", 0),
        "cs": target_player.get("totalMinionsKilled", 0) + target_player.get("neutralMinionsKilled", 0),
        
        "summoner1Id": target_player.get("summoner1Id"),
        "summoner2Id": target_player.get("summoner2Id"),
        
        "primaryStyle": target_player.get("perks", {}).get("styles", [{}])[0].get("selections", [{}])[0].get("perk"),
        "subStyle": target_player.get("perks", {}).get("styles", [{}, {}])[1].get("style"),
        
        "items": [
            target_player.get("item0", 0),
            target_player.get("item1", 0),
            target_player.get("item2", 0),
            target_player.get("item3", 0),
            target_player.get("item4", 0),
            target_player.get("item5", 0),
            target_player.get("item6", 0), # Trinket
        ],
        
        "teams": [team_100, team_200]
    }

async def get_player_dashboard_data(session, region: str, riot_id: str, db: AsyncSession):
    # 1. Get PUUID
    riot_id_parts = riot_id.split("-")
    puuid = await request_puuid_by_summoner_id(session, riot_id, region, RIOT_KEY)
    
    # 2. Get Summoner & League Info
    summoner_info = await get_summoner_info(session, puuid, region, RIOT_KEY)
    league_info = await get_league_info(session, puuid, region, RIOT_KEY)
    
    solo_queue = next((l for l in league_info if l.get("queueType") == "RANKED_SOLO_5x5"), None)
    profile = {
        "gameName": riot_id_parts[0],
        "tagLine": riot_id_parts[1] if len(riot_id_parts) > 1 else "",
        "profileIconId": summoner_info.get("profileIconId"),
        "summonerLevel": summoner_info.get("summonerLevel"),
        "tier": solo_queue.get("tier", "UNRANKED") if solo_queue else "UNRANKED",
        "rank": solo_queue.get("rank", "") if solo_queue else "",
        "lp": solo_queue.get("leaguePoints", 0) if solo_queue else 0,
        "wins": solo_queue.get("wins", 0) if solo_queue else 0,
        "losses": solo_queue.get("losses", 0) if solo_queue else 0,
    }

    # 3. Get Matches
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

    matches = [db_matches[m_id] for m_id in match_ids if m_id in db_matches]
    
    # Parse matches
    parsed_matches = [parse_match_detailed(m, puuid) for m in matches if m]
    parsed_matches = [m for m in parsed_matches if m is not None]

    return {
        "profile": profile,
        "matches": parsed_matches,
        "puuid": puuid
    }

async def get_full_match_data(session, region: str, riot_id: str, db: AsyncSession):
    """Fetch full match JSON data for a player. Reuses existing logic. Restored for chat.py"""
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
