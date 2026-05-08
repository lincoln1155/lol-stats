import pytest
from app.services.riot_service import parse_match_detailed


def _make_fake_match(target_puuid="player-1"):
    return {
        "metadata": {"matchId": "BR1_1234567890"},
        "info": {
            "queueId": 420,
            "gameCreation": 1700000000000,
            "gameDuration": 1800,
            "participants": [
                {
                    "puuid": target_puuid,
                    "teamId": 100,
                    "riotIdGameName": "Faker",
                    "riotIdTagline": "T1",
                    "championName": "Azir",
                    "kills": 10,
                    "deaths": 2,
                    "assists": 5,
                    "totalMinionsKilled": 200,
                    "neutralMinionsKilled": 20,
                    "win": True,
                    "summoner1Id": 4,
                    "summoner2Id": 14,
                    "item0": 6653, "item1": 3020, "item2": 3157,
                    "item3": 3089, "item4": 3135, "item5": 0, "item6": 3340,
                    "perks": {
                        "styles": [
                            {"selections": [{"perk": 8230}]},
                            {"style": 8200},
                        ]
                    },
                },
                {
                    "puuid": "ally-1",
                    "teamId": 100,
                    "riotIdGameName": "Ally",
                    "riotIdTagline": "BR1",
                    "championName": "Lulu",
                },
                {
                    "puuid": "enemy-1",
                    "teamId": 200,
                    "riotIdGameName": "Enemy",
                    "riotIdTagline": "BR1",
                    "championName": "Zed",
                },
            ],
        },
    }


def test_parse_match_detailed_extracts_target_player_stats():
    fake_match = _make_fake_match(target_puuid="player-1")

    result = parse_match_detailed(fake_match, puuid="player-1")

    assert result["matchId"] == "BR1_1234567890"
    assert result["queueName"] == "Ranked Solo"
    assert result["championName"] == "Azir"
    assert result["kills"] == 10
    assert result["deaths"] == 2
    assert result["assists"] == 5
    assert result["cs"] == 220
    assert result["win"] is True
    assert result["items"] == [6653, 3020, 3157, 3089, 3135, 0, 3340]
    assert result["primaryStyle"] == 8230
    assert result["subStyle"] == 8200


def test_parse_match_detailed_splits_teams_by_teamId():
    fake_match = _make_fake_match(target_puuid="player-1")

    result = parse_match_detailed(fake_match, puuid="player-1")

    team_100, team_200 = result["teams"]
    assert {p["championName"] for p in team_100} == {"Azir", "Lulu"}
    assert [p["championName"] for p in team_200] == ["Zed"]


def test_parse_match_detailed_returns_none_when_target_puuid_missing():
    fake_match = _make_fake_match(target_puuid="someone-else")

    result = parse_match_detailed(fake_match, puuid="player-1")

    assert result is None
