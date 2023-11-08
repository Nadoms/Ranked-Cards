import requests
from datetime import timedelta

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
        if not match["is_decay"]:
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
        if not match["is_decay"]:
            if not season:
                if match["winner"] != uuid and match["winner"]:
                    losses += 1
                    if match["forfeit"] == True:
                        forfeits += 1
            elif match["match_season"] == current_season:
                if match["winner"] != uuid and match["winner"]:
                    losses += 1
                    if match["forfeit"] == True:
                        forfeits += 1

    if losses == 0:
        return "-"
    
    forfeit_loss = round(forfeits / losses * 100, 1)
    return forfeit_loss

def get_avg_completion(matches, season, uuid, name):
    current_season = get_season()
    total_time = 0
    completions = 0

    for match in matches:
        if match["winner"] == uuid and match["forfeit"] == False:
            if not season:
                total_time += match["final_time"]
                completions += 1
            elif match["match_season"] == current_season:
                total_time += match["final_time"]
                completions += 1

    if completions == 0:
        return 0
    
    avg_completion = round(total_time / completions, 0)
    return avg_completion

def get_season():
    return 3
"""
    response = requests.get("https://mcsrranked.com/api/matches/?count=1").json()["data"]
    season = response[0]["match_season"]
    return season
"""