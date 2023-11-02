from src.card_functions import add_boxes, add_name, add_stats, \
                               add_podium, add_skin, add_badge, \
                               add_splits, add_socials, add_other

import requests
from PIL import Image
from os import path
from datetime import datetime

def __main__(name, response, discord, pfp):
    if response["status"] != "error":
        response = response["data"]
        uuid = response["uuid"]
        file = path.join("src", "pics", "bgs", "grass.jpg")
        card = Image.open(file)

        then = datetime.now()
        add_boxes.write(card, name, response)
        then = splits(then, 0)
        add_name.write(card, name, response)
        then = splits(then, 1)
        add_stats.write(card, name, uuid, response)
        then = splits(then, 2)
        add_podium.write(card, name, response)
        then = splits(then, 3)
        add_skin.write(card, uuid)
        then = splits(then, 4)
        add_badge.write(card, name, response)
        then = splits(then, 5)
        add_splits.write(card, name)
        then = splits(then, 6)
        add_socials.write(card, name, discord, pfp, response)
        then = splits(then, 7)
        add_other.write(card, name)
        then = splits(then, 8)
        return card
    else:
        print("Player not found.")

def splits(then, process):
    processes = ["Drawing boxes",
     "Writing username",
     "Calculating stats",
     "Pasting podium",
     "Finding skin",
     "Creating badge",
     "Averaging splits",
     "Getting socials",
     "Final touchups"]
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{processes[process]} took {diff}ms")
    return now