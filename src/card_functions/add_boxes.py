from PIL import ImageDraw
import requests

from src.gen_functions import word
from src.card_functions import add_name

def write(card, name, response):
    boxed_image = ImageDraw.Draw(card)
    for box in get_boxes(name, response):
        boxed_image.rectangle(box, fill="#122b30", outline="#000000", width=10) #88cd34
    
    return card

def get_boxes(name, response):
    boxes = [[1350, 50, 1827, 380], [1350, 500, 1827, 830], [70, 820, 650, 1140], get_name_box(name, response)]
    for box in boxes:
        box[0] -= 40
        box[1] -= 30
        box[2] += 40
        box[3] += 30
    return boxes

def get_name_box(name, response):
    length = 130 + min(max(word.calc_length(name, min(word.calc_size(name, 1080), 140)), word.calc_length(add_name.get_activity(response), 35)), 1080)
    box = [70, 50, length, 310]
    return box