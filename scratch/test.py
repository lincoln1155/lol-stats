import os
import urllib.request
import json
import urllib.error

key = os.environ.get("RIOT_API_KEY")
url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/kanaki/kaan?api_key={key}"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    response = urllib.request.urlopen(req)
    print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.reason)
    print(e.read().decode('utf-8'))
