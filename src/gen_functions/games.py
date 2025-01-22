import time
from datetime import timedelta, datetime
import asyncio
from itertools import chain

from gen_functions import api
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
            matches = await asyncio.gather(
                *[
                    api.UserMatches(
                        name=name,
                        page=page,
                        type=2,
                        season=s,
                        excludedecay=not decays
                    ).get_async()
                    for page in range(i, i + step_size)
                ]
            )
            master_matches += list(chain.from_iterable(matches))
            if [] in matches:
                break
            i += step_size

    process_split(then, "Gathering data")
    return master_matches


def get_playtime(response, season_or_total):
    playtime = response["statistics"][season_or_total]["playtime"]["ranked"]

    hours = round(timedelta(milliseconds=playtime).total_seconds() / 3600, 1)
    return hours


def get_playtime_day(response):
    playtime_day = (
        response["statistics"]["total"]["playtime"]["ranked"]
        / (time.time() - response["timestamp"]["firstOnline"])
        / 1000
    )

    minutes = round(playtime_day * 24 * 60, 1)
    return minutes


def get_ff_loss(response, season_or_total):
    forfeits = response["statistics"][season_or_total]["forfeits"]["ranked"]
    losses = max(response["statistics"][season_or_total]["loses"]["ranked"], 1)
    forfeit_loss = forfeits / losses

    forfeit_loss = round(forfeits / losses * 100, 1)
    return forfeit_loss


def get_avg_completion(response, season_or_total):
    completion_time = response["statistics"][season_or_total]["completionTime"][
        "ranked"
    ]
    completions = max(
        response["statistics"][season_or_total]["completions"]["ranked"], 1
    )

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

    while True:
        response = api.UserMatches(
            name=name,
            page=i,
            type=2,
            season=season
        ).get()

        games_left = target_games - num_games
        if games_left <= 49 and len(response) > games_left:
            response = response[0:games_left]

        api.Match.load_db()
        matches = await asyncio.gather(
            *[
                api.Match(id=match["id"]).get_async()
                for match in response
            ]
        )
        api.Match.save_db()

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
        return num_comps, -1  # Not enough completions this season

    process_split(then, "Gathering data")
    return num_comps, detailed_matches


def get_season():
    return 7
