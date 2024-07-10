from datetime import datetime

import requests
from PIL import Image

from analysis_functions import get_skin, get_comments, split_insights, ow_insights
from gen_functions import games

def main(response):
    response = response["data"]
    uuid = response["uuid"]
    name = response["nickname"]
    elo = response["eloRate"]
    if elo == -1:
        return -3

    split_polygon = Image.new("RGB", (400, 400), "#313338")
    ow_polygon = Image.new("RGB", (400, 400), "#313338")

    then = datetime.now()
    detailed_matches = games.get_detailed_matches(response, name, uuid, 30, 100)
    if detailed_matches in (-1, -2):
        return detailed_matches
    then = splits(then, 0)
    skin = get_skin.main(uuid)
    then = splits(then, 1)
    general_comments = get_comments.main(response, detailed_matches)
    then = splits(then, 2)
    split_comm, split_polygon = split_insights.main(uuid, detailed_matches, elo)
    then = splits(then, 3)
    ow_comm, ow_polygon = ow_insights.main(uuid, detailed_matches)
    then = splits(then, 4)
    # polygons = combine.main(split_polygon, ow_polygon)

    comments = {"general": general_comments, "splits": split_comm, "ow": ow_comm}

    return skin, comments, split_polygon, ow_polygon

def splits(then, process):
    processes = ["Collecting data",
    "Finding skin",
    "Generating insights",
    "Constructing split polygon",
    "Constructing overworld polygon",
    "Final touchups"]
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{processes[process]} took {diff}ms")
    return now

if __name__ == "__main__":
    INPUT_NAME = "Nadoms"
    glob_response = requests.get(f"https://mcsrranked.com/api/users/{INPUT_NAME}", timeout=10).json()
    main(glob_response).show()
