from PIL import ImageDraw
from PIL import ImageFont
import requests
from math import floor
from datetime import datetime

from gen_functions import word

def write(analysis, names, response):
    named_image = ImageDraw.Draw(analysis)
    x_values = [610, 1310]

    for i in range(0, 2):
        name_size = min(word.calc_size(names[i], 550), 120)
        name_font = ImageFont.truetype('minecraft_font.ttf', name_size)
        x = int(x_values[i] + (i-1) * word.calc_length(names[i], name_size))
        y = int(120 - word.horiz_to_vert(name_size) / 2)
        
        named_image.text((x, y), names[i], font=name_font, fill="#ffffff")
    return analysis