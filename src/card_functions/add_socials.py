from io import BytesIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
import requests
from os import path

from src.gen_functions import word

def write(card, name, discord, pfp, response):
    discord = get_discord(discord)
    discord_size = min(word.calc_size(discord, 520), 50)
    discord_font = ImageFont.truetype('minecraft_font.ttf', discord_size)

    twitch = get_twitch(response)
    twitch_size = min(word.calc_size(twitch, 470), 30)
    twitch_font = ImageFont.truetype('minecraft_font.ttf', twitch_size)
    
    socialed_image = ImageDraw.Draw(card)
    socialed_image.text((1700-word.calc_length(discord, discord_size), 935-discord_size/2), discord, font=discord_font, fill="#ffffff", stroke_width=4, stroke_fill="#000000")
    # socialed_image.text((1650-word.calc_length(get_yt(response), 25), 1035), get_yt(response), font=yt_font, fill="#ff0000", stroke_width=2, stroke_fill="#ffffff")
    socialed_image.text((1650-word.calc_length(twitch, twitch_size), 1075-twitch_size/2), twitch, font=twitch_font, fill="#9146ff", stroke_width=2, stroke_fill="#ffffff")
    write_pfp(card, 1750, pfp)
    # write_yt(card)
    write_twitch(card)

    return card

def get_discord(discord):
    if discord == "notnaddysalt":
        discord = "Unlinked"
    else:
        discord = "@" + discord
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

    file = path.join("src", "pics", "other", "circle.png")
    circle = Image.open(file).convert("L")

    pic = Image.open(BytesIO(response.content)).convert("RGBA")

    circled_pic = ImageOps.fit(pic, circle.size, centering=(0.5, 0.5))
    circled_pic.putalpha(circle)
    circled_pic = circled_pic.resize((120, 120))

    card.paste(circled_pic, (x, y), circled_pic)
    return card

def write_discord(card):
    pass

def write_yt(card):
    file = path.join("src", "pics", "other", "yt_logo.png")
    yt = Image.open(file)
    yt = yt.resize((40, 40))
    card.paste(yt, (1665, 1035), yt)

def write_twitch(card):
    file = path.join("src", "pics", "other", "twitch_logo.png")
    twitch = Image.open(file)
    twitch = twitch.resize((40, 40))
    card.paste(twitch, (1665, 1065), twitch)