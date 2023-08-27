import requests
from datetime import timedelta

def get_matches(name, season):
    matches = []
    if season:
        response = ["PLACEHOLDER"]
        i = 0
        while response != []:
            response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page={i}&count=50&filter=2").json()["data"]
            matches += response
            i += 1
        return matches
    for s in range(0,5):
        response = ["PLACEHOLDER"]
        i = 0
        while response != []:
            response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page={i}&count=50&filter=2&season={s}").json()["data"]
            matches += response
            i += 1
    return matches

def get_playtime(name, season):
    matches = get_matches(name, season)
    playtime = 0
    for match in matches:
        playtime += match["final_time"]
    hours = round(timedelta(milliseconds=playtime).total_seconds() / 3600, 1)
    return hours

def get_ff_loss(name, season):
    uuid = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]["uuid"]
    matches = get_matches(name, season)
    forfeits = 0
    losses = 0
    for match in matches:
        if match["winner"] != uuid:
            losses += 1
            if match["forfeit"] == True:
                forfeits += 1
    forfeit_loss = round(forfeits / losses * 100, 1)
    return forfeit_loss