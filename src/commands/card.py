from os import path
from datetime import datetime

import requests
from PIL import Image, ImageFilter

from card_functions import add_boxes, add_history, add_name, add_stats, \
                               add_podium, add_skin, add_badge, \
                               add_socials, add_other
from gen_functions import games
from gen_functions.word import process_split


def main(name, response, discord, pfp, background, history):
    response = response["data"]
    uuid = response["uuid"]
    winstreak = response["statistics"]["season"]["currentWinStreak"]["ranked"]

    file = path.join("src", "pics", "bgs", "used", background)
    card = Image.open(file).convert("RGBA").filter(ImageFilter.GaussianBlur(0))

    then = datetime.now()
    card = add_boxes.write(card, name, response)
    then = process_split(then, "Drawing boxes")
    add_name.write(card, name, response)
    then = process_split(then, "Writing username")
    add_stats.write(card, response)
    then = process_split(then, "Calculating stats")
    add_podium.write(card, response)
    then = process_split(then, "Pasting podium")
    add_skin.write(card, uuid)
    then = process_split(then, "Finding skin")
    add_badge.write(card, response)
    then = process_split(then, "Creating badge")
    add_history.write(card, history, uuid, winstreak)
    then = process_split(then, "Checking history")
    add_socials.write(card, discord, pfp, response)
    then = process_split(then, "Getting socials")
    add_other.write(card)
    then = process_split(then, "Final touchups")
    return card

if __name__ == "__main__":
    INPUT_NAME = "nadoms"
    RESPONSE = requests.get(f"https://mcsrranked.com/api/users/{INPUT_NAME}", timeout=10).json()
    DISCORD = "notnaddysalt"
    PFP = "https://cdn.discordapp.com/avatars/343108228890099713/1b4bf25c894af2c68410b0574135d150"
    BACKGROUND = "bastion.jpg"
    main(INPUT_NAME, RESPONSE, DISCORD, PFP, BACKGROUND)
