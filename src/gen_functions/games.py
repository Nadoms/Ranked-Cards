import time
from datetime import timedelta, datetime
import asyncio
from pprint import pp
from itertools import chain

import numpy as np
import requests
import aiohttp

from gen_functions.word import process_split


async def get_matches(name, season, decays):
    then = datetime.now()
    master_matches = []
    step_size = 5

    if season == "Lifetime":
        seasons = range(get_season(), 0, -1)
    else:
        seasons = [season]

    for s in seasons:
        i = 0
        while True:
            matches = await asyncio.gather(*[get_user_matches(name=name, season=s, decays=decays, page=page) for page in range(i, i+step_size)])
            master_matches += list(chain.from_iterable(matches))
            if [] in matches:
                break
            i += step_size

    process_split(then, "Gathering data")
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

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                response_data = await response.json()
        except asyncio.TimeoutError:
            return None

        if isinstance(response, str):
            return None
        if response_data["status"] == "success":
            return response_data["data"]
        return None


def get_last_match(name):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    player_response = requests.get(f"https://mcsrranked.com/api/users/{name}", headers=headers, timeout=10).json()
    if player_response["data"] == "Too many requests":
        return -1

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


async def get_detailed_matches(player_response, season, min_comps, target_games):
    then = datetime.now()
    detailed_matches = []
    num_comps = 0
    num_games = 0
    i = 0

    name = player_response["nickname"]
    uuid = player_response["uuid"]
    response = "PLACEHOLDER"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}

    while True:
        response = requests.get(f"https://mcsrranked.com/api/users/{name}/matches?page={i}&season={season}&count=50&type=2&excludedecay", headers=headers, timeout=10).json()["data"]

        games_left = target_games - num_games
        if games_left <= 49 and len(response) > games_left:
            response = response[0:games_left]

        matches = await asyncio.gather(*[get_match_details(match["id"]) for match in response])
        detailed_matches += matches
        i += 1
        num_games = len(detailed_matches)
        if matches == []:
            break

        if num_games >= target_games:
            break

    for match in detailed_matches:
        if not match["forfeited"] and match["result"]["uuid"] == uuid:
            num_comps += 1

    if num_comps < min_comps and not name == "Nadoms":
        return num_comps, -1 # Not enough completions this season

    process_split(then, "Gathering data")
    return num_comps, detailed_matches


async def get_match_details(match_id):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    url = f"https://mcsrranked.com/api/matches/{match_id}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                response_data = await response.json()
        except asyncio.TimeoutError:
            return None
        if response_data == "Too many requests":
            return None
        if response_data["status"] == "success":
            return response_data["data"]
        return None


def get_match_details_sync(match_id):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    url = f"https://mcsrranked.com/api/matches/{match_id}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except:
        return None
    if isinstance(response, str):
        return None
    if response["status"] == "success":
        return response["data"]
    return None


def get_season():
    """
        response = requests.get("https://mcsrranked.com/api/matches/?count=1").json()["data"]
        season = response[0]["match_season"]
        return season
    """
    return 6


def split(then, name="That"):
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{name} took {diff}ms")
    return now
