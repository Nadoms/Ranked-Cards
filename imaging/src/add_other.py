from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# for when the card was generated

def write(card):
    named_image = ImageDraw.Draw(card)
    name_font = ImageFont.truetype('minecraft_font.ttf', 140)
    named_image.text((120, 90), get_name(), font=name_font, fill=(255, 255, 255))
    
    return card

def get_name():
    return "Nadoms"