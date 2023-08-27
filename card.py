import src.add_boxes
import src.add_name
import src.add_stats
import src.add_podium
import src.add_skin
import src.add_badge
import src.add_splits
import src.add_socials
import src.add_other

import requests
from PIL import Image
from os import path

def __main__(input_name, pfp):
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}").json()

    if response["status"] != "error":
        name = response["data"]["nickname"]
        file = path.join("src", "pics", "bgs", "grass.jpg")
        card = Image.open(file)
        src.add_boxes.write(card, name)
        src.add_name.write(card, name)
        src.add_stats.write(card, name)
        src.add_podium.write(card, name)
        src.add_skin.write(card, name)
        src.add_badge.write(card, name)
        src.add_splits.write(card, name)
        src.add_socials.write(card, name, pfp)
        src.add_other.write(card, name)
        return card
    else:
        print("Player not found.")