import requests
from datetime import timedelta, datetime

def get_matches(name):
    matches = []
    then = datetime.now()
    for s in range(0, get_season()+1):
        response = ["PLACEHOLDER"]
        i = 0
        while response != []:
            response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page={i}&count=50&filter=2&season={s}").json()["data"]
            matches += response
            i += 1
    then = splits(then, 1)
    return matches

def get_playtime(matches, season):
    then = datetime.now()
    current_season = get_season()
    then = splits(then, 2)
    playtime = 0

    for match in matches:
        if not season:
            playtime += match["final_time"]
            continue
        if match["match_season"] == current_season:
            playtime += match["final_time"]

    hours = round(timedelta(milliseconds=playtime).total_seconds() / 3600, 1)
    return hours

def get_ff_loss(matches, season, name):
    then = datetime.now()
    uuid = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]["uuid"]
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
        then = splits(then, 3)
        return 0
    
    forfeit_loss = round(forfeits / losses * 100, 1)
    then = splits(then, 3)
    return forfeit_loss

def splits(then, process):
    processes = ["Getting season matches",
     "Getting lifetime matches",
     "Calculating playtime",
     "Calculating ff/loss"]
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{processes[process]} took {diff}ms")
    return now

def get_season():
    return 2
"""
    response = requests.get("https://mcsrranked.com/api/matches/?count=1").json()["data"]
    season = response[0]["match_season"]
    return season
"""