import json
from os import path


def get_rank(elo):
    if not elo:
        return -1
    if elo < 600:
        return 0
    if elo < 900:
        return 1
    if elo < 1200:
        return 2
    if elo < 1500:
        return 3
    if elo < 2000:
        return 4
    if elo >= 2000:
        return 5
    return -1


def get_colour(elo):
    if not elo:
        return ["#151716", "#ffffff", "#8f8f8f"]
    if elo < 600:
        return ["#151716", "#ffffff", "#8f8f8f"]
    if elo < 900:
        return ["#bdbdbd", "#313338", "#5d5d5d"]
    if elo < 1200:
        return ["#fad43d", "#313338", "#8a740d"]
    if elo < 1500:
        return ["#30e858", "#313338", "#107828"]
    if elo < 2000:
        return ["#37dcdd", "#313338", "#177c7d"]
    if elo >= 2000:
        return ["#3e3a3e", "#fad43d", "#8a741d"]
    return ["#151716", "#ffffff"]


def get_degree(elo):
    degree = 270
    if not elo:
        return degree

    if elo < 600:
        degree += round(elo / 600 * 360)
    elif elo < 1500:
        degree += round((elo % 300) / 300 * 360)
    elif elo < 2000:
        degree += round((elo - 1500) / 500 * 360)
    elif elo >= 2000:
        degree -= 1
    degree %= 360
    return degree


def get_division(elo):
    if not elo:
        return ""

    if elo < 600:
        if elo < 200:
            return "I"
        if elo < 400:
            return "II"
        return "III"

    if elo < 1500:
        diff = elo % 300
        if diff < 100:
            return "I"
        if diff < 200:
            return "II"
        return "III"

    if elo < 2000:
        diff = elo % 500
        if diff < 150:
            return "I"
        if diff < 300:
            return "II"
        return "III"

    return ""


def get_elo_equivalent(value, attr_type):
    fp = path.join("src", "models", "models.json")
    with open(fp, "r", encoding="UTF-8") as f:
        models = json.load(f)

    value *= 10e-7
    model = models[attr_type]

    elo = model["a"] / (value + model["b"]) + model["c"]
    elo = round(elo * 10e2)

    return elo
