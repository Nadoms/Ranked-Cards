from datetime import datetime

import requests
from PIL import Image

from match_functions import add_info, add_names, add_shapes, add_stats, add_skins, add_splits, add_other


def main(response):
    response = response["data"]
    names = [response["players"][0]["nickname"], response["players"][1]["nickname"]]
    uuids = [response["players"][0]["uuid"], response["players"][1]["uuid"]]

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    vs_response = requests.get(f"https://mcsrranked.com/api/users/{names[0]}/versus/{names[1]}", headers=headers, timeout=10).json()
    if vs_response["status"] != "success":
        return -1
    vs_response = vs_response["data"]

    chart = Image.new("RGB", (1200, 1920), "#313338")

    then = datetime.now()
    chart = add_shapes.write(chart)
    then = splits(then, 0)
    chart = add_names.write(chart, names, response)
    then = splits(then, 1)
    chart = add_stats.write(chart, uuids, response, vs_response)
    then = splits(then, 2)
    chart = add_skins.write(chart, uuids)
    then = splits(then, 3)
    chart = add_splits.write(chart, uuids, response)
    then = splits(then, 4)
    chart = add_info.write(chart, response)
    then = splits(then, 5)
    chart = add_other.write(chart)
    then = splits(then, 6)

    return chart


def splits(then, process):
    processes = ["Drawing boxes",
     "Writing usernames",
     "Calculating stats",
     "Finding skins",
     "Comparing splits",
     "Adding seed info",
     "Final touchups"]
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{processes[process]} took {diff}ms")
    return now
