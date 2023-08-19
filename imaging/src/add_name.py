from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def write(card):
    name_font = ImageFont.truetype('minecraft_font.ttf', 140)
    activity_font = ImageFont.truetype('minecraft_font.ttf', 35)
    

    named_image = ImageDraw.Draw(card)
    named_image.text((120, 90), get_name(), font=name_font, fill=(255, 255, 255))
    named_image.text((120, 270), get_activity(), font=activity_font, fill=(255, 255, 255))

    return card

def get_name():
    return "Nadoms"

def get_activity():
    last_active = "2 days ago"
    return f"Last Active: {last_active}"