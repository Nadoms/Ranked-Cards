from io import BytesIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
import requests
from math import floor
from datetime import datetime

from . import word

def write(card, name, pfp):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]

    discord_font = ImageFont.truetype('minecraft_font.ttf', 50)
    twitch_yt_font = ImageFont.truetype('minecraft_font.ttf', 25)
    
    socialed_image = ImageDraw.Draw(card)
    socialed_image.text((1700-word.calc_length(get_discord(response, name), 50), 910), get_discord(response, name), font=discord_font, fill="#ffffff", stroke_width=4, stroke_fill="#000000")
    socialed_image.text((1650-word.calc_length(get_yt(response), 25), 1035), get_yt(response), font=twitch_yt_font, fill="#ff0000", stroke_width=2, stroke_fill="#ffffff")
    socialed_image.text((1650-word.calc_length(get_twitch(response), 25), 1075), get_twitch(response), font=twitch_yt_font, fill="#9146ff", stroke_width=2, stroke_fill="#ffffff")
    write_pfp(card, 1750, pfp)
    write_yt(card)
    write_twitch(card)

    return card

def get_discord(response, name):
    discord = "Unlinked"
    with open (r"src\link.txt", "r") as f:
        for line in f:
            if name in line:
                discord = "@" + line.split(":")[1]
                break
    return discord

def get_yt(response):
    if response["connections"]["youtube"]:
        youtube = response["connections"]["youtube"]["name"]
        return youtube
    else:
        return "Unlinked"

def get_twitch(response):
    if response["connections"]["twitch"]:
        twitch = response["connections"]["twitch"]["name"]
        return "twitch.tv/" + twitch
    else:
        return "Unlinked"
    
def write_pfp(card, x, pfp):
    response = requests.get(pfp)
    y = 880

    pfped_image = ImageDraw.Draw(card)
    pfped_image.ellipse([x-6, y-6, x+124, y+125], fill="#122b30", outline="#000000", width=2)

    circle = Image.open(r"src\pics\other\circle.png").convert("L")

    pic = Image.open(BytesIO(response.content))

    circled_pic = ImageOps.fit(pic, circle.size, centering=(0.5, 0.5))
    circled_pic.putalpha(circle)
    circled_pic = circled_pic.resize((120, 120))

    card.paste(circled_pic, (x, y), circled_pic)
    return card

def write_discord(card):
    pass

def write_yt(card):
    yt = Image.open(r"C:\Users\Ntakr\VSCode\Ranked-Cards\src\pics\other\yt_logo.png")
    yt = yt.resize((40, 40))
    card.paste(yt, (1665, round(1035)), yt)

def write_twitch(card):
    twitch = Image.open(r"C:\Users\Ntakr\VSCode\Ranked-Cards\src\pics\other\twitch_logo.png")
    twitch = twitch.resize((40, 40))
    card.paste(twitch, (1665, round(1075)), twitch)