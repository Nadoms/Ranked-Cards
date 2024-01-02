from PIL import ImageDraw, ImageFont
import requests

from gen_functions import word

def write(analysis, names, response):
    shaped_image = ImageDraw.Draw(analysis)
    info_size = 20
    info_font = ImageFont.truetype('minecraft_font.ttf', info_size)

    for line in get_lines():
        shaped_image.line(line, fill="#cccccc", width=5)

    texts_pos = get_text_pos()
    for i in range(len(texts_pos[0])):
        x = 960 - word.calc_length(texts_pos[0][i], info_size) / 2
        y = texts_pos[1][i] - int(word.horiz_to_vert(info_size) / 2)
        shaped_image.text((x, y), texts_pos[0][i], font=info_font, fill="#ffff00")

    for box in get_boxes(names, response):
        shaped_image.rectangle(box, fill="#122b30", outline="#000000", width=10) #88cd34
    
    return analysis

def get_lines():
    lines = []
    x = 960
    spacing = 20

    top_y = 20
    bottom_y = 1180

    coords = [top_y] + get_text_pos()[1] + [bottom_y]
    for i in range(len(coords)):
        if i != 0:
            lines.append([(x, coords[i-1]+spacing), (x, coords[i]-spacing)])
    return lines

def get_text_pos():
    pos = [120, 250, 320, 390]
    texts = ["vs", "elo", "rank", "score"]
    return [texts, pos]

def get_boxes(names, response):
    boxes = []
    for box in boxes:
        box[0] -= 40
        box[1] -= 30
        box[2] += 40
        box[3] += 30
    return boxes