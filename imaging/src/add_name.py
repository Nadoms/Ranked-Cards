from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]

    name_font = ImageFont.truetype('minecraft_font.ttf', 140)
    activity_font = ImageFont.truetype('minecraft_font.ttf', 35)
    
    named_image = ImageDraw.Draw(card)
    named_image.text((100, 50), name, font=name_font, fill=(255, 255, 255))
    named_image.text((100, 230), get_activity(response), font=activity_font, fill=(255, 255, 255))

    return card

def get_activity(response):
    last_active = response["latest_time"]
    return f"Last Active: {last_active}"