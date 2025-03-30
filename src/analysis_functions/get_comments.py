import json
import math
from os import path
from pathlib import Path

import numpy as np

from gen_functions import games, rank, numb
from gen_functions.word import percentify
from gen_functions.rank import Rank


def main(response, elo, season, rank_filter):
    general_comments = {}
    general_comments["title"] = (
        f"Analysis of `{response['nickname']}` in Season {season}"
    )
    general_comments["description"] = (
        "This is how you stack up against the playerbase."
        f"\nAll playerbase comparisons will update daily using all season {season} matches."
    )

    if not elo:
        general_comments["elo"] = [f"ELO: `-`"]
    else:
        general_comments["elo"] = [
            f"ELO: `{elo}`",
            percentify(get_attr_ranked(elo, "elo", rank_filter)),
            get_elo_info(elo, "elo"),
        ]
    avg = games.get_avg_completion(response, "season")
    if avg == 0:
        general_comments["avg"] = [f"Avg Finish: `-`"]
        general_comments["sb"] = [f"Avg Finish: `-`"]
    else:
        sb = int(response["statistics"]["season"]["bestTime"]["ranked"])
        general_comments["avg"] = [
            f"Avg Finish: `{numb.digital_time(avg)}`",
            percentify(get_attr_ranked(avg, "avg", rank_filter)),
            f"Equivalent to {rank.get_elo_equivalent(avg, 'avg')} ELO",
        ]
        general_comments["sb"] = [
            f"Season Best: `{numb.digital_time(sb)}`",
            percentify(get_attr_ranked(sb, "sb", rank_filter)),
            f"Equivalent to {rank.get_elo_equivalent(sb, 'sb')} ELO",
        ]
    ffl = games.get_ff_loss(response, "season")
    general_comments["ffl"] = [f"Forfeit/Loss `{ffl}%`", get_ffl_comments(ffl)]

    return general_comments


def get_attr_ranked(value, attr_type, rank_filter):
    playerbase_file = Path("src") / "database" / "playerbase.json"
    with open(playerbase_file, "r") as f:
        attrs = json.load(f)[attr_type]
    if attr_type == "elo":
        attrs = list(reversed(attrs))

    if rank_filter:
        lower, upper = rank.get_boundaries(rank_filter)
        attrs = [
            attr[0]
            for attr in attrs
            if lower <= attr[1] < upper
        ]

    ranked_attr = round(np.searchsorted(attrs, value) / len(attrs), 3)
    if attr_type != "elo":
        ranked_attr = 1 - ranked_attr
    return ranked_attr


def get_elo_info(elo):
    tier = [rank.RANKS[rank.get_rank(elo)], rank.get_division(elo)]
    return f"{tier[0]} {tier[1]}"


def get_ffl_comments(ffl):
    ffl_comments = [
        "Absolutely unyielding 👑",
        "Will persevere as long as there's a chance.",
        "Good mental while not afraid to go next.",
        "Willing to take some Ls for sanity.",
        "Could try playing more seeds out.",
        "Despair...",
    ]

    segment_size = 100 / (len(ffl_comments) - 1)
    index = math.ceil(ffl / segment_size)
    if ffl == 100:
        index = -1

    return ffl_comments[index]
