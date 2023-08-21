from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests

from . import word
from . import add_name

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]

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
    length = 130 + max(word.calc_length(name, 140), word.calc_length(add_name.get_activity(response), 35))
    box = [70, 50, length, 310]
    return box