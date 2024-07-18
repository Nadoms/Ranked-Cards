from datetime import datetime

import requests
from PIL import Image

from match_functions import add_info, add_names, add_shapes, add_stats, add_skins, add_splits, add_other
from gen_functions.word import process_split


def main(response):
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
