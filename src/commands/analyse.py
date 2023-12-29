from analyse_functions import add_boxes, add_names, add_stats, add_skins, add_splits, add_context, add_pentagon, add_other

import requests
from PIL import Image
from os import path
from datetime import datetime

def main(uuid, response, match_id):
    names = [response["members"][0]["nickname"], response["members"][1]["nickname"]]
    file = path.join("src", "pics", "bgs", "grass.jpg")
    analysis = Image.open(file)

    then = datetime.now()
    analysis = add_boxes.write(analysis, names, response)
    then = splits(then, 0)
    analysis = add_names.write(analysis, names, response)
    then = splits(then, 1)
    analysis = add_stats.write(analysis, names, response, match_id)
    then = splits(then, 2)
    analysis = add_skins.write(analysis, names, response)
    then = splits(then, 3)
    analysis = add_splits.write(analysis, names, response, match_id)
    then = splits(then, 4)
    analysis = add_context.write(analysis, names, response, match_id)
    then = splits(then, 5)
    analysis = add_pentagon.write(analysis, names, response, match_id)
    then = splits(then, 6)
    analysis = add_other.write(analysis, names, response)
    then = splits(then, 7)

    return analysis

def splits(then, process):
    processes = ["Drawing boxes",
     "Writing usernames",
     "Calculating stats",
     "Finding skins",
     "Comparing splits",
     "Generating context",
     "Pentagoning pentgagon",
     "Final touchups"]
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{processes[process]} took {diff}ms")
    return now

if __name__ == "__main__":
    input_name = "nadoms"
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}").json()
    type = "elo"
    main(input_name, response, type).show()