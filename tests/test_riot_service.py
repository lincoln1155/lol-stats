import pytest
from app.services.riot_service import process_match_data

def test_process_match_data_success():
    # 1. Arrange (Prepare a mock JSON, simulating Riot API response)
    fake_match_data = {
        'info': {
            'participants': [
                {
                    'puuid': '12345',
                    'riotIdGameName': 'Faker',
                    'riotIdTagline': 'T1',
                    'individualPosition': 'MID',
                    'championName': 'Azir',
                    'kills': 10, 'deaths': 2, 'assists': 5,
                    'goldEarned': 15000,
                    'totalMinionsKilled': 200, 'neutralMinionsKilled': 20,
                    'win': True
                }
            ]
        }
    }
    
    # 2. Act (Execute the function that should extract the data)
    resultado = process_match_data(fake_match_data, puuid='12345')
    
    # 3. Assert (Verify if the result matches the expected output)
    assert resultado['username'] == 'Faker#T1'
    assert resultado['kda'] == '10/2/5'
    assert resultado['cs'] == 220
    assert resultado['win'] == True
    assert resultado['champion'] == 'Azir'
    assert resultado['role'] == 'MID'
