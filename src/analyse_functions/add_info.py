from datetime import datetime, timedelta
from math import floor
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from os import path

from gen_functions import word

def write(analysis, response):
    x_values = [880, 960, 1040]
    y = 90

    seed = get_seed(response)
    seed_x = round(x_values[1] - seed.size[0] / 2)
    seed_y = round(y - seed.size[1] / 2)
    analysis.paste(seed, (seed_x, seed_y), seed)

    infoed_image = ImageDraw.Draw(analysis)
    info_size = 25
    id_size = 20
    info_font = ImageFont.truetype('minecraft_font.ttf', info_size)
    id_font = ImageFont.truetype('minecraft_font.ttf', id_size)

    text_y = round(y - word.horiz_to_vert(info_size) / 2)

    date = get_delta(response)
    left_text = f"Played {date}"
    left_x = x_values[0] - word.calc_length(left_text, info_size)
    infoed_image.text((left_x, text_y), left_text, font=info_font, fill="lightblue")

    time = get_time(response)
    result = get_result(response)
    right_text = f"Seed {result} at {time}"
    right_x = x_values[2]
    infoed_image.text((right_x, text_y), right_text, font=info_font, fill="lightblue")

    id = f"Match #{response['id']}"
    id_x = x_values[1] - word.calc_length(id, id_size) / 2
    id_y = round(y - word.horiz_to_vert(id_size) / 2) - 60
    infoed_image.text((id_x, id_y), id, font=id_font, fill="yellow")


    return analysis

def get_seed(response):
    seed_type = response["seedType"].lower()
    file = path.join("src", "pics", "stuctures", f"{seed_type}.png")
    seed = Image.open(file)
    seed = seed.resize((60, 60), resample=Image.NEAREST)
    return seed

def get_delta(response):
    date = response["date"]
    delta_date = datetime.now() - datetime.fromtimestamp(date)
    if delta_date.days >= 1:
        return f"{delta_date.days} day(s) ago"
    elif delta_date.total_seconds() / 3600 >= 1:
        return f"{floor(delta_date.total_seconds() / 3600)} hour(s) ago"
    else:
        return f"{floor(delta_date.total_seconds() / 60)} minute(s) ago"
    
def get_time(response):
    time = response["result"]["time"]
    time = str(timedelta(milliseconds=time))[2:7].lstrip("0")
    return time

def get_result(response):
    if response["forfeited"]:
        return "forfeited"
    elif response["result"]["uuid"]:
        return "completed"
    else:
        return "drawn"