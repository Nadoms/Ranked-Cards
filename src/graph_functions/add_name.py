from PIL import ImageDraw
from PIL import ImageFont

from gen_functions import word

def write(graph, name):
    name_size = min(word.calc_size(name, 300), 35)
    name_font = ImageFont.truetype('minecraft_font.ttf', name_size)
    
    named_image = ImageDraw.Draw(graph)
    named_image.text((125, 50-name_size), name, font=name_font, fill="#ffffff")

    return graph