from PIL import ImageDraw, ImageFont
import requests

from . import rank

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]
    
    splits_font = ImageFont.truetype('minecraft_font.ttf', 20)
    
    splitted_image = ImageDraw.Draw(card)
    splitted_image.text((200, 700), "Average splits - work in progress", font=splits_font, fill="white")

    return card