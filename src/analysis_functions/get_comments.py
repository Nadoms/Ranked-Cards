import json
import math
from os import path

import numpy as np

from gen_functions import games
from gen_functions.word import percentify

def main(response, detailed_matches):
    elo = int(response["eloRate"])
    avg = games.get_avg_completion(response, "season")
    sb = int(response["statistics"]["season"]["bestTime"]["ranked"])
    ffl = games.get_ff_loss(response, "season")

    comments = {}
    comments["title"] = f"Analysis of {response['nickname']}'s last {len(detailed_matches)} matches"
    comments["description"] = "This is how you stack up against the playerbase."
    comments["general"] = {}
    comments["general"]["elo"] = [f"{elo} ELO", percentify(get_attr_ranked(elo, 'elo'))]
    comments["general"]["avg"] = [f"{avg} Avg Finish", percentify(get_attr_ranked(avg, 'avg')), f"Equiv. to {get_elo_equivalent(avg, 'avg')} ELO"]
    comments["general"]["sb"] = [f"{sb} Season Best", percentify(get_attr_ranked(sb, 'sb')), f"Equiv. to {get_elo_equivalent(sb, 'sb')} ELO"]
    comments["general"]["ffl"] = [f"{ffl}% Forfeit/Loss", get_ffl_comments(ffl)]

    print(comments)
    return comments


def get_attr_ranked(value, attr_type):
    attr_mapping = {
        "avg": "avg",
        "sb": "sb_vs_elo",
        "elo": "elo",
    }

    fp = path.join("src", "database", "mcsrstats", f"{attr_mapping[attr_type]}.txt")
    attrs = []
    with open(fp, "r") as f:
        while True:
            attr = f.readline().strip().split()
            if not attr:
                break
            attrs.append(int(attr[0]))
            
    ranked_attr = round(np.searchsorted(attrs, value) / len(attrs), 3)
    if attr_type == "elo":
        ranked_attr = 1 - ranked_attr
    print(ranked_attr)
    return ranked_attr

def get_elo_equivalent(value, attr_type):

    fp = path.join("src", "models", "models.json")
    with open(fp, "r") as f:
        models = json.load(f)

    value *= 10e-7
    model = models[attr_type]
    print(model, value)

    elo = model["a"] / (value + model["b"]) + model["c"]
    elo = round(elo * 10e2)

    return elo


def get_ffl_comments(ffl):
    ffl_comments = ["NUTTY mental",
                    "Very persistent and consistent player",
                    "Good mental while not afraid to go next",
                    "Willing to take some Ls for sanity",
                    "Should try playing more seeds out",
                    "Despair"]
    
    segment_size = 100 / (len(ffl_comments)-1)
    index = math.ceil(ffl / segment_size)
    if ffl == 100:
        index = -1

    return ffl_comments[index]