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
    response = requests.get(url).json()
    return response['puuid']

info = get_summoner_info()

key = load_key()

request_puuid_by_summoner_id(info[0], info[1], key)

# push test