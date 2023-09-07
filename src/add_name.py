from PIL import ImageDraw
from PIL import ImageFont
import requests
from math import floor
from datetime import datetime

from . import word

def write(card, name, response):
    name_size = min(word.calc_size(name, 1080), 140)
    name_font = ImageFont.truetype('minecraft_font.ttf', name_size)
    activity_font = ImageFont.truetype('minecraft_font.ttf', 35)
    
    named_image = ImageDraw.Draw(card)
    named_image.text((100, 190-name_size), name, font=name_font, fill="#ffffff")
    named_image.text((100, 230), get_activity(response), font=activity_font, fill="#ffffff")

    return card

def get_activity(response):
    last_active = response["latest_time"]
    active_date = datetime.fromtimestamp(last_active)
    current_date = datetime.now()
    delta_date = current_date - active_date
    if delta_date.days >= 1:
        return f"Last Active: {delta_date.days} day(s) ago"
    elif delta_date.total_seconds() / 3600 >= 1:
        return f"Last Active: {floor(delta_date.total_seconds() / 3600)} hour(s) ago"
    else:
        return f"Last Active: {floor(delta_date.total_seconds() / 60)} minute(s) ago"