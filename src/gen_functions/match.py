import requests
from datetime import timedelta

def get_matches(name, season):
    if season == "Lifetime":
        matches = []
        for s in reversed(range(1, get_season()+1)):
            matches += get_season_matches(name, s)
    else:
        if not season:
            season = get_season()
        matches = get_season_matches(name, season)
    return matches

def get_season_matches(name, s):
    matches = []
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    response = ["PLACEHOLDER"]
    i = 0
    while response != []:
        if response == "Too many requests":
            return None
        response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page={i}&count=50&filter=2&season={s}", headers=headers).json()["data"]
        matches += response
        i += 1
    return matches

def get_recent_matches(name):
    matches = []
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page=0&count=50&filter=2&season={get_season()}", headers=headers).json()["data"]
    matches += response
    return matches

def get_last_match(name):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    player_response = requests.get(f"https://mcsrranked.com/api/users/{name}", headers=headers).json()
    if player_response["status"] == "error":
        return None
    uuid = player_response["data"]["uuid"]
    
    matches_response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?count=1&filter=2&excludedecay", headers=headers).json()
    if matches_response["data"] == []:
        return None
    else:
        return [uuid, matches_response["data"][0]["match_id"]]

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
    return 4
"""
    response = requests.get("https://mcsrranked.com/api/matches/?count=1").json()["data"]
    season = response[0]["match_season"]
    return season
"""