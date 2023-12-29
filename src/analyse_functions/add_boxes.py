from PIL import ImageDraw
import requests

from gen_functions import word
from graph_functions import add_name

def write(graph, names, response):
    boxed_image = ImageDraw.Draw(graph)
    for box in get_boxes(names, response):
        boxed_image.rectangle(box, fill="#122b30", outline="#000000", width=10) #88cd34
    
    return graph

def get_boxes(names, response):
    boxes = []
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