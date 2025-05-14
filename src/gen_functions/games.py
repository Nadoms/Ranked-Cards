import time
from datetime import timedelta, datetime
import asyncio
from itertools import chain

from gen_functions import api, constants
from gen_functions.word import process_split


def get_matches(name, season, decays, limit=None):
    then = datetime.now()
    master_matches = []

    if season == "Lifetime":
        s = constants.SEASON
    else:
        s = season

    last_id = 100000000
    while limit is None or len(master_matches) < limit:
        matches = api.UserMatches(
            name=name,
            before=last_id,
            type=2,
            season=s,
            excludedecay=not decays
        ).get()
        if matches == []:
            if season == "Lifetime" and s > 1:
                s -= 1
            else:
                break
        master_matches += matches
        last_id = matches[-1]["id"]

    process_split(then, "Gathering matches")
    return master_matches if limit is None else master_matches[:limit]


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


async def get_detailed_matches(player_response, season, min_comps, limit):
    then = datetime.now()
    detailed_matches = []
    num_comps = 0
    num_games = 0

    name = player_response["nickname"]
    uuid = player_response["uuid"]
    response = "PLACEHOLDER"

    brief_matches = get_matches(name, season, decays=False, limit=limit)
    step = 100

    for i in range(0, len(brief_matches), step):
        detailed_matches += await asyncio.gather(
            *[
                api.Match(id=match["id"]).get_async()
                for match in brief_matches[i : i + step]
            ]
        )
        api.Match.commit()

    for match in detailed_matches:
        if not match["forfeited"] and match["result"]["uuid"] == uuid:
            num_comps += 1

    if num_comps < min_comps and not name == "Nadoms":
        return num_comps, -1  # Not enough completions this season

    process_split(then, "Gathering match details")
    return num_comps, detailed_matches
