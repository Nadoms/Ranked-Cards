from datetime import datetime
from math import floor
from os import path

from PIL import Image, ImageDraw, ImageFont

from gen_functions import numb, word


def write(chart, response):
    middle = 600
    x_values = [middle - 80, middle, middle + 80]
    y = 90

    seed = get_seed(response)
    seed_x = round(x_values[1] - seed.size[0] / 2)
    seed_y = round(y - seed.size[1] / 2)
    chart.paste(seed, (seed_x, seed_y), seed)

    infoed_image = ImageDraw.Draw(chart)
    info_size = 25
    id_size = 20
    info_font = ImageFont.truetype("minecraft_font.ttf", info_size)
    id_font = ImageFont.truetype("minecraft_font.ttf", id_size)

    text_y = round(y - word.horiz_to_vert(info_size) / 2)

    date = get_delta(response)
    left_text = f"Played {date}"
    left_x = x_values[0] - word.calc_length(left_text, info_size)
    infoed_image.text((left_x, text_y), left_text, font=info_font, fill="lightblue")

    time = numb.digital_time(response["result"]["time"])
    result = get_result(response)
    right_text = f"Seed {result} at {time}"
    right_x = x_values[2]
    infoed_image.text((right_x, text_y), right_text, font=info_font, fill="lightblue")

    match_id = f"Match #{response['id']}"
    id_x = x_values[1] - word.calc_length(match_id, id_size) / 2
    id_y = round(y - word.horiz_to_vert(id_size) / 2) - 60
    infoed_image.text((id_x, id_y), match_id, font=id_font, fill="yellow")

    return chart


def get_seed(response):
    seed_type = response["seedType"].lower()
    file = path.join("src", "pics", "stuctures", f"{seed_type}.png")
    seed = Image.open(file)
    seed = seed.resize((80, 80), resample=Image.NEAREST)
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


def get_result(response):
    if response["forfeited"]:
        return "forfeited"
    if response["result"]["uuid"]:
        return "completed"
    return "drawn"
