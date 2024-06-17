import math

from gen_functions import games

def main(response, detailed_matches):
    elo = response["eloRate"]
    avg = games.get_avg_completion(response, "season")
    pb = response["statistics"]["total"]["bestTime"]
    ffl = games.get_ff_loss(response, "season")

    comments = {}
    comments["title"] = f"Analysis of {response['nickname']}'s last {len(detailed_matches)} matches"
    comments["description"] = "ballsack"
    comments["general"] = {}
    comments["general"]["elo"] = [f"{elo} ELO", f"Top {get_attr_ranked(elo, 'elo')}%"]
    comments["general"]["avg"] = [f"{avg} Avg Finish", f"Top {get_attr_ranked(avg, 'avg')}%", f"Equiv. to {get_elo_equivalent(avg, 'avg')} ELO"]
    comments["general"]["pb"] = [f"{pb} PB", f"Top {get_attr_ranked(pb, 'pb')}%", f"Equiv. to {get_elo_equivalent(pb, 'pb')} ELO"]
    comments["general"]["ffl"] = [f"{ffl}% Forfeit/Loss", get_ffl_comments(ffl)]

def get_attr_ranked(value, attr_type):
    return 30

def get_elo_equivalent(value, attr_type):
    return 1600

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