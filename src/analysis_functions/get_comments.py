import json
import math
from os import path

import numpy as np

from gen_functions import games, rank, numb
from gen_functions.word import percentify


def main(response, elo, season):
    general_comments = {}
    general_comments["title"] = f"Analysis of `{response['nickname']}` in Season {season}"
    general_comments["description"] = (
        "This is how you stack up against the playerbase. "
        f"This section has been updated to use your stats from the specified season, S{season}."
        "\nComparisons of any statistic are made against players who have at least 5 counts of the statistic in season 6."
    )

    if not elo:
        general_comments["elo"] = [f"ELO: `-`"]
    else:
        general_comments["elo"] = [
            f"ELO: `{elo}`",
            percentify(get_attr_ranked(elo, "elo")),
            get_elo_equivalent(elo, "elo"),
        ]
    avg = games.get_avg_completion(response, "season")
    if avg == 0:
        general_comments["avg"] = [f"Avg Finish: `-`"]
        general_comments["sb"] = [f"Avg Finish: `-`"]
    else:
        sb = int(response["statistics"]["season"]["bestTime"]["ranked"])
        general_comments["avg"] = [
            f"Avg Finish: `{numb.digital_time(avg)}`",
            percentify(get_attr_ranked(avg, "avg")),
            f"Equivalent to {get_elo_equivalent(avg, 'avg')} ELO",
        ]
        general_comments["sb"] = [
            f"Season Best: `{numb.digital_time(sb)}`",
            percentify(get_attr_ranked(sb, "sb")),
            f"Equivalent to {get_elo_equivalent(sb, 'sb')} ELO",
        ]
    ffl = games.get_ff_loss(response, "season")
    general_comments["ffl"] = [f"Forfeit/Loss `{ffl}%`", get_ffl_comments(ffl)]

    return general_comments


def get_attr_ranked(value, attr_type):
    attr_mapping = {
        "avg": "avg_vs_elo",
        "sb": "sb_vs_elo",
        "elo": "elo",
    }

    fp = path.join("src", "database", "mcsrstats", f"{attr_mapping[attr_type]}.txt")
    attrs = []
    with open(fp, "r", encoding="UTF-8") as f:
        while True:
            attr = f.readline().strip().split()
            if not attr:
                break
            attrs.append(int(attr[0]))

    ranked_attr = round(np.searchsorted(attrs, value) / len(attrs), 3)
    if attr_type != "elo":
        ranked_attr = 1 - ranked_attr
    return ranked_attr


def get_elo_equivalent(value, attr_type):
    ranks = ["Coal", "Iron", "Gold", "Emerald", "Diamond", "Netherite", "Unranked"]

    if attr_type == "elo":
        tier = [ranks[rank.get_rank(value)], rank.get_division(value)]
        return f"{tier[0]} {tier[1]}"

    fp = path.join("src", "models", "models.json")
    with open(fp, "r", encoding="UTF-8") as f:
        models = json.load(f)

    value *= 10e-7
    model = models[attr_type]

    elo = model["a"] / (value + model["b"]) + model["c"]
    elo = round(elo * 10e2)

    return elo


def get_ffl_comments(ffl):
    ffl_comments = [
        "NUTTY mental!?",
        "Very persistent and consistent player!",
        "Good mental while not afraid to go next.",
        "Willing to take some Ls for sanity.",
        "Should try playing more seeds out.",
        "Despair...",
    ]

    segment_size = 100 / (len(ffl_comments) - 1)
    index = math.ceil(ffl / segment_size)
    if ffl == 100:
        index = -1

    return ffl_comments[index]
