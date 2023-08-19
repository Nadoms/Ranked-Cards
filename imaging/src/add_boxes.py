from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from . import word

def write(card, name):
    boxed_image = ImageDraw.Draw(card)
    for box in get_boxes(name):
        boxed_image.rectangle(box, fill="#122b30", outline="#000000", width=15) #88cd34
    
    return card

def get_boxes(name):
    boxes = [[1350, 50, 1827, 380], [1350, 500, 1827, 830], [70, 820, 650, 1140], get_name_box(name)]
    for box in boxes:
        box[0] -= 30
        box[1] -= 20
        box[2] += 30
        box[3] += 20
    return boxes

def get_name_box(name):
    box = [70, 50, 130+word.calc_length(name, 140), 305]
    return box