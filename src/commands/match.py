from datetime import datetime

import requests
from PIL import Image

from gen_functions import api
from match_functions import (
    add_info,
    add_names,
    add_shapes,
    add_stats,
    add_skins,
    add_splits,
    add_other,
)
from gen_functions.word import process_split


def main(response):
    season = response["season"]
    names = [response["players"][0]["nickname"], response["players"][1]["nickname"]]
    uuids = [response["players"][0]["uuid"], response["players"][1]["uuid"]]
    vs_response = api.Versus(name_1=uuids[0], name_2=uuids[1], season=season).get()

    chart = Image.new("RGBA", (1200, 1920), (30, 33, 36, 0))

    then = datetime.now()
    chart = add_shapes.write(chart)
    then = process_split(then, "Drawing boxes")
    chart = add_names.write(chart, names, response)
    then = process_split(then, "Writing usernames")
    chart = add_stats.write(chart, uuids, response, vs_response)
    then = process_split(then, "Calculating stats")
    chart = add_skins.write(chart, uuids)
    then = process_split(then, "Finding skins")
    chart = add_splits.write(chart, uuids, response)
    then = process_split(then, "Comparing splits")
    chart = add_info.write(chart, response)
    then = process_split(then, "Adding seed info")
    chart = add_other.write(chart)
    then = process_split(then, "Final touchups")

    return chart
