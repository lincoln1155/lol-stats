import os
import requests
from dotenv import load_dotenv

def load_key():
    load_dotenv(".env")
    SECRET_KEY = os.environ.get("RIOT_API_KEY")
    return SECRET_KEY


def get_summoner_info():
    print("Insert your region")
    print("[1] Americas | [2] Asia | [3] Europe ")
    region = int(input())
    
    if region == 1:
        region = "americas"
    elif region == 2:
        region = "asia"
    elif region == 3:
        region = "europe"


    print("Now insert your summmoner ID, as in player#tag")
    summoner_id = input()
    summoner_id = summoner_id.split("#", 1)

    return summoner_id, region


def request_puuid_by_summoner_id(summoner_id, region, key):
    
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_id[0]}/{summoner_id[1]}?api_key={key}"
    puuid = requests.get(url).json()
    return puuid['puuid']
    

def get_matchid_by_puuid(puuid, region, key):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={key}"
    match_ids = requests.get(url).json()
    return match_ids[0]

def get_match_data_by_id(match_id, region, key):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={key}"
    match_data = requests.get(url).json()
    return match_data

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
            }
            return stats
    return None


info = get_summoner_info()

key = load_key()

puuid = request_puuid_by_summoner_id(info[0], info[1], key)

match_id = get_matchid_by_puuid(puuid, info[1], key)

match_data = get_match_data_by_id(match_id, info[1], key)

player_stats = process_match_data(match_data, puuid)

print(player_stats)