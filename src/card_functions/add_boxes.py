from PIL import ImageDraw, Image
import requests

from gen_functions import word
from card_functions import add_name

def write(card, name, response):
    boxed_card = card.copy()
    boxed_image = ImageDraw.Draw(boxed_card)

    for box in get_boxes(name, response):
        boxed_image.rectangle(box, fill="#000000") #122b30

    card = Image.blend(card, boxed_card, 0.6)
    outlined_image = ImageDraw.Draw(card)

    for box in get_boxes(name, response):
        outlined_image.rectangle(box, outline="#000000", width=8)
    
    return card

def get_boxes(name, response):
    boxes = [[1350, 50, 1827, 380], [1350, 480, 1827, 810], [70, 820, 650, 1140], get_name_box(name, response)]
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