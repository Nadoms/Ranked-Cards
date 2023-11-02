import requests
from datetime import timedelta

def get_split_mactches(name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?count=50&filter=2").json()["data"]
    return response

def get_matches(name):
    matches = []
    for s in range(0, get_season()+1):
        response = ["PLACEHOLDER"]
        i = 0
        while response != []:
            response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page={i}&count=50&filter=2&season={s}").json()["data"]
            matches += response
            i += 1
    return matches

def get_recent_matches(name):
    matches = []
    response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page=0&count=50&filter=2&season={get_season()}").json()["data"]
    matches += response
    return matches

def get_playtime(matches, season):
    current_season = get_season()
    playtime = 0

    for match in matches:
        if not season:
            playtime += match["final_time"]
            continue
        if match["match_season"] == current_season:
            playtime += match["final_time"]

    hours = round(timedelta(milliseconds=playtime).total_seconds() / 3600, 1)
    return hours

def get_ff_loss(matches, season, uuid, name):
    current_season = get_season()
    forfeits = 0
    losses = 0

    for match in matches:
        if not season:
            if match["winner"] != uuid:
                losses += 1
                if match["forfeit"] == True:
                    forfeits += 1
            continue
        if match["match_season"] == current_season:
            if match["winner"] != uuid:
                losses += 1
                if match["forfeit"] == True:
                    forfeits += 1

    if losses == 0:
        return 0
    
    forfeit_loss = round(forfeits / losses * 100, 1)
    return forfeit_loss

def get_season():
    return 3
"""
    response = requests.get("https://mcsrranked.com/api/matches/?count=1").json()["data"]
    season = response[0]["match_season"]
    return season
"""