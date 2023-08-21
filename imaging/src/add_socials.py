from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests
from math import floor
from datetime import datetime

from . import word

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]

    discord_font = ImageFont.truetype('minecraft_font.ttf', 50)
    twitch_yt_font = ImageFont.truetype('minecraft_font.ttf', 25)
    
    socialed_image = ImageDraw.Draw(card)
    socialed_image.text((1700-word.calc_length(get_discord(response, card), 50), 900), get_discord(response, card), font=discord_font, fill="#ffffff", stroke_width=5, stroke_fill="#000000")
    socialed_image.text((1650-word.calc_length(get_yt(response, card), 25), 1035), get_yt(response, card), font=twitch_yt_font, fill="#ff0000", stroke_width=2, stroke_fill="#ffffff")
    socialed_image.text((1650-word.calc_length(get_twitch(response, card), 25), 1075), get_twitch(response, card), font=twitch_yt_font, fill="#9146ff", stroke_width=2, stroke_fill="#ffffff")

    return card

def get_discord(response, card):
    # Check if user is linked
    if response["connections"]["discord"]:
        discord = response["connections"]["discord"]["name"]
        write_pfp(card)
        return "@" + discord
    else:
        return "Discord not linked"

def get_yt(response, card):
    if response["connections"]["youtube"]:
        youtube = response["connections"]["youtube"]["name"]
        write_yt(card)
        return youtube
    else:
        return ""

def get_twitch(response, card):
    if response["connections"]["twitch"]:
        twitch = response["connections"]["twitch"]["name"]
        write_twitch(card)
        return "twitch.tv/" + twitch
    else:
        return ""
    
def write_pfp(card):
    pass

def write_discord(card):
    pass

def write_yt(card):
    yt = Image.open(r"C:\Users\Ntakr\VSCode\Ranked-Cards\imaging\src\pics\other\yt_logo.png")
    yt = yt.resize((40, 40))
    card.paste(yt, (1665, round(1035)), yt)

def write_twitch(card):
    twitch = Image.open(r"C:\Users\Ntakr\VSCode\Ranked-Cards\imaging\src\pics\other\twitch_logo.png")
    twitch = twitch.resize((40, 40))
    card.paste(twitch, (1665, round(1075)), twitch)