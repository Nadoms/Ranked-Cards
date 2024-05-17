from card_functions import add_boxes, add_history, add_name, add_stats, \
                               add_podium, add_skin, add_badge, \
                               add_socials, add_other

import requests
import random
from PIL import Image, ImageFilter
from os import path
from datetime import datetime

from gen_functions import match

def main(name, response, discord, pfp):
    response = response["data"]
    uuid = response["uuid"]
    pics = ["beach.jpg", "bastion.jpg", "fort.jpg", "portal.jpg", "stronghold.jpg", "end.jpg"]
    pic = pics[random.randint(0,5)]
    # if random.randint(0, 100) == 0:
    #     pic = "end.jpg"
    file = path.join("src", "pics", "bgs", "custom", pic)
    card = Image.open(file).convert("RGBA").filter(ImageFilter.GaussianBlur(0))

    then = datetime.now()
    matches = match.get_recent_matches(name, False)
    then = splits(then, 0)
    card = add_boxes.write(card, name, response)
    then = splits(then, 1)
    add_name.write(card, name, response)
    then = splits(then, 2)
    add_stats.write(card, response)
    then = splits(then, 3)
    add_podium.write(card, name, response)
    then = splits(then, 4)
    add_skin.write(card, uuid)
    then = splits(then, 5)
    add_badge.write(card, response)
    then = splits(then, 6)
    add_history.write(card, matches, uuid, response)
    then = splits(then, 7)
    add_socials.write(card, name, discord, pfp, response)
    then = splits(then, 8)
    add_other.write(card, name)
    then = splits(then, 9)
    return card

def splits(then, process):
    processes = ["Gathering data",
     "Drawing boxes",
     "Writing username",
     "Calculating stats",
     "Pasting podium",
     "Finding skin",
     "Creating badge",
     "Checking history",
     "Getting socials",
     "Final touchups"]
    now = datetime.now()
    diff = round((now - then).total_seconds() * 1000)
    print(f"{processes[process]} took {diff}ms")
    return now

if __name__ == "__main__":
    input_name = "nadoms"
    response = requests.get(f"https://mcsrranked.com/api/users/{input_name}").json()
    discord = "notnaddysalt"
    pfp = "https://cdn.discordapp.com/avatars/343108228890099713/1b4bf25c894af2c68410b0574135d150"
    main(input_name, response, discord, pfp)