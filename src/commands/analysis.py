from analysis_functions import get_skin, get_comments, split_insights, ow_insights

import requests
from PIL import Image
from os import path
from datetime import datetime

from gen_functions import games

def main(response):
    response = response["data"]
    uuid = response["uuid"]
    name = response["nickname"]

    split_penta = Image.new("RGB", (400, 400), "#313338")
    ow_penta = Image.new("RGB", (400, 400), "#313338")

    then = datetime.now()
    detailed_matches = games.get_detailed_matches(name, uuid, 0, 42)
    if detailed_matches == -1:
        return -1
    then = splits(then, 0)
    skin = get_skin.main(uuid)
    then = splits(then, 1)
    comments = get_comments.main(response, detailed_matches)
    then = splits(then, 2)
    split_comm, split_penta = split_insights.main(uuid, detailed_matches)
    then = splits(then, 3)
    ow_comm, ow_penta = ow_insights.main(detailed_matches)
    then = splits(then, 4)

    text = {"general": comments, "splits": split_comm, "ow": ow_comm}

    return skin, text, split_penta, ow_penta

def splits(then, process):
    processes = ["Collecting data",
     "Finding skin",
     "Generating insights",
     "Constructing split pentagon",
     "Constructing overworld pentagon",
     "Final touchups"]
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{processes[process]} took {diff}ms")
    return now

if __name__ == "__main__":
    input_name = "Nadoms"
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}").json()
    main(response).show()