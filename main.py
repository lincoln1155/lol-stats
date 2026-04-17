import os
import requests
import asyncio
import aiohttp
from dotenv import load_dotenv

MAX_CONCURRENT_REQUESTS = 10
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

def load_key():
    load_dotenv(".env")
    SECRET_KEY = os.environ.get("RIOT_API_KEY")
    return SECRET_KEY


def get_summoner_info():
    print("Insert your region")
    print("[1] Americas | [2] Asia | [3] Europe ")
    
    region_map = {'1': 'americas', '2': 'asia', '3': 'europe'}
    
    choice = input('>> ')
    region = region_map.get(choice)

    print("Now insert your summmoner ID (player#tag)")
    summoner_id = input('>> ')
    summoner_id = summoner_id.split("#", 1)

    return summoner_id, region

async def request_puuid_by_summoner_id(session, summoner_id, region, key):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_id[0]}/{summoner_id[1]}?api_key={key}"
    
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
            if response.status == '429':
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
                'result': player['win']
            }
            return stats
    return None



async def main():
    key = load_key()
    summoner_id, region = get_summoner_info()
    
    async with aiohttp.ClientSession() as session:
        print("Searching...")

        puuid = await request_puuid_by_summoner_id(session, summoner_id, region, key)

        match_ids = await get_matchid_by_puuid(session, puuid, region, key)

        tasks = [get_match_data_by_id(session, m_id, region, key) for m_id in match_ids]

        all_matches = await asyncio.gather(*tasks)
    print(f"Last 20 matches: for {summoner_id[0]}#{summoner_id[1]}")
    for match in all_matches:
        stats = process_match_data(match, puuid)
        if stats:
            print(f"Role: {stats['role']}, Win: {stats['result']}, Champion: {stats['champion']}, KDA: {stats['kda']}, CS: {stats['cs']}")

if __name__ == "__main__":
    asyncio.run(main())