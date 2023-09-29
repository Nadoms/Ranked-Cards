from PIL import ImageDraw, ImageFont
import requests

from src.gen_functions import rank, match

def write(card, name):
    splits_font = ImageFont.truetype('minecraft_font.ttf', 20)
    
    splitted_image = ImageDraw.Draw(card)
    splitted_image.text((200, 700), "Average splits - work in progress", font=splits_font, fill="white")

    return card