import time
from datetime import timedelta
import asyncio
from pprint import pp

import requests


def get_matches(name, season, decays):
    if season == "Lifetime":
        matches = []
        for s in reversed(range(1, get_season()+1)):
            matches += asyncio.run(get_season_matches(name, s, decays))
    else:
        if not season:
            season = get_season()
        matches = asyncio.run(get_season_matches(name, season, decays))
    return matches


async def get_season_matches(name, season, decays):
    master_matches = []
    i = 0
    step_size = 5

    while True:
        matches = await asyncio.gather(*[get_user_matches(name=name, season=season, decays=decays, page=page) for page in range(i, i+step_size)])
        master_matches += filter(lambda a: a != [], matches)
        if [] in matches:
            break
        i += step_size
    return master_matches


async def get_user_matches(name:str, page:int=0, count:int=50, m_type:int=2, season:int=-1, decays:bool=False):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}

    if not decays:
        excludedecay = "&excludedecay"
    else:
        excludedecay = ""
    if season == -1:
        season = get_season()

    url = f"https://mcsrranked.com/api/users/{name}/matches?page={page}&count={count}&type={m_type}&season={season}{excludedecay}"

    try:
        response = requests.get(url, headers=headers, timeout=10).json()
    except TimeoutError:
        return None

    if response == "Too many requests":
        return None
    if response["status"] == "success":
        return response["data"]
    return None


def get_last_match(name):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    player_response = requests.get(f"https://mcsrranked.com/api/users/{name}", headers=headers, timeout=10).json()
    if player_response["status"] == "error":
        return None

    matches_response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?count=1&type=2&excludedecay", headers=headers, timeout=10).json()
    if matches_response["data"] == []:
        return None

    return matches_response["data"][0]["id"]


def get_playtime(response, season_or_total):
    playtime = response["statistics"][season_or_total]["playtime"]["ranked"]

    hours = round(timedelta(milliseconds=playtime).total_seconds() / 3600, 1)
    return hours


def get_playtime_day(response):
    playtime_day = response["statistics"]["total"]["playtime"]["ranked"] / (time.time() - response["timestamp"]["firstOnline"]) / 1000

    minutes = round(playtime_day * 24 * 60, 1)
    return minutes


def get_ff_loss(response, season_or_total):
    forfeits = response["statistics"][season_or_total]["forfeits"]["ranked"]
    losses = max(response["statistics"][season_or_total]["loses"]["ranked"], 1)
    forfeit_loss = forfeits / losses

    forfeit_loss = round(forfeits / losses * 100, 1)
    return forfeit_loss


def get_avg_completion(response, season_or_total):
    completion_time = response["statistics"][season_or_total]["completionTime"]["ranked"]
    completions = max(response["statistics"][season_or_total]["completions"]["ranked"], 1)

    avg_completion = round(completion_time / completions)
    return avg_completion


def get_detailed_matches(player_response, name, uuid, min_comps, target_games):
    detailed_matches = []
    num_comps = 0
    num_games = 0
    i = 0
    s = get_season()

    season_comps = player_response["statistics"]["season"]["completions"]["ranked"]
    season_games = player_response["statistics"]["season"]["playedMatches"]["ranked"]
    if season_comps < min_comps / 2:
        return -1 # Not enough completions this season
    if season_comps / season_games < 0.15:
        return -2 # Ratio of completions to played matches is too low
    
    response = "PLACEHOLDER"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}

    while s >= get_season() - 1:
        response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page={i}&season={s}&count=50&type=2&excludedecay", headers=headers, timeout=10).json()["data"]

        for match in response:
            match_id = match["id"]
            match_response = requests.get(f"https://mcsrranked.com/api/matches/{match_id}", headers=headers, timeout=10).json()["data"]
            detailed_matches.append(match_response)
            num_games += 1

            if match_response["forfeited"] is False and match_response["result"]["uuid"] == uuid:
                num_comps += 1

            if num_games >= target_games and num_comps >= min_comps:
                return detailed_matches
                
        i += 1

        if response == []:
            i = 0
            s -= 1

    if num_comps == 0:
        return -1

    return detailed_matches


def get_season():
    """
        response = requests.get("https://mcsrranked.com/api/matches/?count=1").json()["data"]
        season = response[0]["match_season"]
        return season
    """
    return 5
