import json
import math
from os import path
from pathlib import Path

import numpy as np

from rankedutils import constants, games, insight, rank, numb
from rankedutils.word import percentify


PLAYERBASE_FILE = Path("src") / "database" / "playerbase.json"
COMMENTS = {
    "ffl": {
        0: "Absolutely unyielding 👑",
        20: "Will persevere as long as there's a chance.",
        40: "Good mental while not afraid to go next.",
        60: "Willing to take some Ls for sanity.",
        80: "Could try playing more seeds out.",
        100: "Despair...",
    },
    "cmpr": {
        10: "", # Barely ever finishes a game.",
        20: "", # Gets to see the end sometimes.",
        30: "", # Worth knowing zero at this point.",
        40: "", # Consistent throughout the run.",
        50: "", # Highly confident in completing seeds.",
        100: "", # Plays ranked like no-reset.",
    },
    "trwr": {
        10: "", # Can't get more consistent.",
        25: "", # Goes deathless most games.",
        40: "", # Throws easy wins pretty often.",
        55: "", # Needs to work on playing safer.",
        100: "", # Stop dying!!!!",
    },
}


def main(response, detailed_matches, elo, season, rank_filter):
    general_comments = {}
    comparison_str = "" if rank_filter is None else f" - {rank_filter} Comparison"
    general_comments["title"] = (
        f"Analysis of `{response['nickname']}` in S{season}{comparison_str}"
    )
    playerbase_str = "the entire playerbase" if rank_filter is None else f"{rank_filter} players"
    general_comments["description"] = (
        f"This is how you stack up against {playerbase_str}. Each comparison references at most {get_player_count(rank_filter)} players."
        f"\nClick [here](https://docs.google.com/document/d/1hbz_lTBF0GdIKL_tEVhB2XFj3ZtWIvrRSakYXAk9fwU/edit?usp=sharing) for an explanation of this command."
    )

    if not elo:
        general_comments["elo"] = [f"Elo: `-`"]
    else:
        general_comments["elo"] = [
            f"Elo: `{elo}`",
            percentify(get_attr_ranked(elo, "elo", rank_filter)),
            get_elo_info(elo),
        ]
    avg = games.get_avg_completion(response, "season")
    sb = int(response["statistics"]["season"]["bestTime"]["ranked"])
    general_comments["avg"] = [
        f"Avg Finish: `{numb.digital_time(avg)}`",
        percentify(get_attr_ranked(avg, "avg", rank_filter)),
        f"Equivalent to {rank.get_elo_equivalent(avg, 'avg')} Elo",
    ]
    general_comments["sb"] = [
        f"Season Best: `{numb.digital_time(sb)}`",
        percentify(get_attr_ranked(sb, "sb", rank_filter)),
        f"Equivalent to {rank.get_elo_equivalent(sb, 'sb')} Elo",
    ]
    ffl = games.get_ff_loss(response, "season")
    general_comments["ffl"] = [f"Forfeit/Loss: `{ffl}%`", get_comments(ffl, "ffl")]
    cmpr = games.get_completion_rate(response, "season")
    general_comments["cmpr"] = [f"Completion Rate: `{cmpr}%`", get_comments(cmpr, "cmpr")]
    trwr = insight.get_throw_rate(response["uuid"], detailed_matches)
    general_comments["trwr"] = [f"Throw Rate: `{trwr}%`", get_comments(trwr, "trwr")]

    return general_comments


def get_player_count(rank_filter):
    with open(PLAYERBASE_FILE, "r") as f:
        elos = json.load(f)["elo"]
    lower, upper = rank.get_boundaries(rank_filter)
    player_count = sum(1 for elo in elos if lower <= elo < upper)
    return player_count


def get_attr_ranked(value, attr_type, rank_filter):
    with open(PLAYERBASE_FILE, "r") as f:
        attrs = json.load(f)[attr_type]
    if attr_type == "elo":
        attrs = list(reversed(attrs))

    lower, upper = rank.get_boundaries(rank_filter)
    if attr_type == "elo":
        attrs = [attr for attr in attrs if lower <= attr < upper]
    else:
        attrs = [
            attr[0]
            for attr in attrs
            if rank_filter is None or (attr[1] and lower <= attr[1] < upper)
        ]
    if not attrs:
        raise LookupError("No players found in this rank to compare to.")

    ranked_attr = round(np.searchsorted(attrs, value) / len(attrs), 3)
    if attr_type != "elo":
        ranked_attr = 1 - ranked_attr
    return ranked_attr


def get_elo_info(elo):
    tier = [rank.RANKS[rank.get_rank(elo)], rank.get_division(elo)]
    return f"{tier[0]} {tier[1]}"


def get_comments(value, attr):
    for threshold in COMMENTS[attr]:
        if value <= threshold:
            return COMMENTS[attr][threshold]
    raise ValueError(f"Value {value} for {attr} is not within bounds.")
