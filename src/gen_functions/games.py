import time
import requests
from datetime import timedelta


def get_matches(name, season, decays):
    if season == "Lifetime":
        matches = []
        for s in reversed(range(1, get_season()+1)):
            matches += get_season_matches(name, s, decays)
    else:
        if not season:
            season = get_season()
        matches = get_season_matches(name, season, decays)
    return matches


def get_season_matches(name, s, decays):
    matches = []
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    response = ["PLACEHOLDER"]

    if not decays:
        excludedecay = "&excludedecay"
    else:
        excludedecay = ""

    i = 0
    while response != []:
        if response == "Too many requests":
            return None
        response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page={i}&count=50&type=2&season={s}{excludedecay}", headers=headers).json()["data"]
        matches += response
        i += 1
    return matches


def get_recent_matches(name, decays):
    matches = []
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}

    if not decays:
        excludedecay = "&excludedecay"
    else:
        excludedecay = ""

    response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page=0&count=50&type=2&season={get_season()}{excludedecay}", headers=headers).json()["data"]
    matches += response
    return matches


def get_last_match(name):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    player_response = requests.get(f"https://mcsrranked.com/api/users/{name}", headers=headers).json()
    if player_response["status"] == "error":
        return None
    uuid = player_response["data"]["uuid"]
    
    matches_response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?count=1&type=2&excludedecay", headers=headers).json()
    if matches_response["data"] == []:
        return None
    else:
        return [uuid, matches_response["data"][0]["id"]]


def get_playtime(response, seasonOrTotal):
    playtime = response["statistics"][seasonOrTotal]["playtime"]["ranked"]

    hours = round(timedelta(milliseconds=playtime).total_seconds() / 3600, 1)
    return hours


def get_playtime_day(response):
    playtime_day = response["statistics"]["total"]["playtime"]["ranked"] / (time.time() - response["timestamp"]["firstOnline"]) / 1000

    minutes = round(playtime_day * 24 * 60, 1)
    return minutes


def get_ff_loss(response, seasonOrTotal):
    forfeits = response["statistics"][seasonOrTotal]["forfeits"]["ranked"]
    losses = max(response["statistics"][seasonOrTotal]["loses"]["ranked"], 1)
    forfeit_loss = forfeits / losses

    forfeit_loss = round(forfeits / losses * 100, 1)
    return forfeit_loss


def get_avg_completion(response, seasonOrTotal):
    completion_time = response["statistics"][seasonOrTotal]["completionTime"]["ranked"]
    completions = max(response["statistics"][seasonOrTotal]["completions"]["ranked"], 1)

    avg_completion = round(completion_time / completions, 1)
    return avg_completion


def get_detailed_matches(name, uuid, min_comps, target_games):
    detailed_matches = []
    num_comps = 0
    num_games = 0
    i = 0
    s = 5
    response = "PLACEHOLDER"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}

    while s >= 4:
        response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page={i}&season={s}&count=50&type=2&excludedecay", headers=headers).json()["data"]

        for match in response:
            match_id = match["id"]
            match_response = requests.get(f"https://mcsrranked.com/api/matches/{match_id}", headers=headers).json()["data"]
            detailed_matches.append(match_response)
            num_games += 1

            if match_response["forfeited"] == False and match_response["result"]["uuid"] == uuid:
                num_comps += 1

            if num_games >= target_games and num_comps >= min_comps:
                print(f"Targets met ({target_games} games and {min_comps} completions)")
                print(f"Extracted {num_games} games including {num_comps} completions")
                return detailed_matches
                
        i += 1

        if response == []:
            i = 0
            s -= 1

    if num_comps == 0:
        return -1
    
    print(f"Targets not met ({target_games} games and {min_comps})")
    print(f"Extracted {num_games} games including {num_comps} completions")

    return detailed_matches


def get_season():
    return 5
    """
        response = requests.get("https://mcsrranked.com/api/matches/?count=1").json()["data"]
        season = response[0]["match_season"]
        return season
    """