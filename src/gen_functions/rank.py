from enum import IntEnum
import json
from os import path


RANKS = ["Coal", "Iron", "Gold", "Emerald", "Diamond", "Netherite", "Unranked"]


class Rank(IntEnum):
    UNRANKED = -1
    COAL = 0
    IRON = 1
    GOLD = 2
    EMERALD = 3
    DIAMOND = 4
    NETHERITE = 5

    def __str__(self):
        return RANKS[self]


def str_to_rank(rank_str):
    if rank_str.lower() == "unranked":
        return None
    if rank_str.lower() == "coal":
        return Rank.COAL
    if rank_str.lower() == "iron":
        return Rank.IRON
    if rank_str.lower() == "gold":
        return Rank.GOLD
    if rank_str.lower() == "emerald":
        return Rank.EMERALD
    if rank_str.lower() == "diamond":
        return Rank.DIAMOND
    if rank_str.lower() == "netherite":
        return Rank.NETHERITE
    return None


def get_rank(elo):
    if not elo:
        return Rank.UNRANKED
    if elo < 600:
        return Rank.COAL
    if elo < 900:
        return Rank.IRON
    if elo < 1200:
        return Rank.GOLD
    if elo < 1500:
        return Rank.EMERALD
    if elo < 2000:
        return Rank.DIAMOND
    if elo >= 2000:
        return Rank.NETHERITE


def get_boundaries(rank: Rank):
    if rank == Rank.UNRANKED:
        return None, None
    if rank == Rank.COAL:
        return 0, 600
    if rank == Rank.IRON:
        return 600, 900
    if rank == Rank.GOLD:
        return 900, 1200
    if rank == Rank.EMERALD:
        return 1200, 1500
    if rank == Rank.DIAMOND:
        return 1500, 2000
    if rank == Rank.NETHERITE:
        return 2000, 3000
    return 0, 3000


def get_colour(elo):
    rank = get_rank(elo)
    if rank == Rank.UNRANKED:
        return ["#151716", "#ffffff", "#8f8f8f"]
    if rank == Rank.COAL:
        return ["#151716", "#ffffff", "#8f8f8f"]
    if rank == Rank.IRON:
        return ["#bdbdbd", "#313338", "#5d5d5d"]
    if rank == Rank.GOLD:
        return ["#fad43d", "#313338", "#8a740d"]
    if rank == Rank.EMERALD:
        return ["#30e858", "#313338", "#107828"]
    if rank == Rank.DIAMOND:
        return ["#37dcdd", "#313338", "#177c7d"]
    if rank == Rank.NETHERITE:
        return ["#3e3a3e", "#fad43d", "#8a741d"]


def get_degree(elo):
    rank = get_rank(elo)
    degree = 270

    if rank == Rank.UNRANKED:
        return degree
    if rank == Rank.COAL:
        degree += round(elo / 600 * 360)
    elif rank <= Rank.EMERALD:
        degree += round((elo % 300) / 300 * 360)
    elif rank == Rank.DIAMOND:
        degree += round((elo - 1500) / 500 * 360)
    elif rank == Rank.NETHERITE:
        degree -= 1
    degree %= 360
    return degree


def get_division(elo):
    rank = get_rank(elo)

    if rank == Rank.UNRANKED or rank == Rank.NETHERITE:
        return ""

    if rank == Rank.COAL:
        if elo < 200:
            return "I"
        if elo < 400:
            return "II"
        return "III"

    if rank == Rank.DIAMOND:
        diff = elo % 500
        if diff < 150:
            return "I"
        if diff < 300:
            return "II"
        return "III"

    diff = elo % 300
    if diff < 100:
        return "I"
    if diff < 200:
        return "II"
    return "III"


def get_elo_equivalent(value, attr_type):
    fp = path.join("src", "models", "models.json")
    with open(fp, "r", encoding="UTF-8") as f:
        models = json.load(f)

    value *= 10e-7
    model = models[attr_type]

    elo = model["a"] / (value + model["b"]) + model["c"]
    elo = round(elo * 10e2)

    return elo


def get_emote(rank: Rank):
    if rank == Rank.COAL:
        return "<:coal_rank:1382105120170446968>"
    if rank == Rank.IRON:
        return "<:iron_rank:1382105118815555614>"
    if rank == Rank.GOLD:
        return "<:gold_rank:1382105117221716009>"
    if rank == Rank.EMERALD:
        return "<:emerald_rank:1382104820470648832>"
    if rank == Rank.DIAMOND:
        return "<:diamond_rank:1382104818260246588>"
    if rank == Rank.NETHERITE:
        return "<:netherite_rank:1382104816523804782>"
    return "<:unranked:1382105122414530621>"
