from PIL import Image, ImageDraw, ImageFont

from gen_functions import word


def write(chart):
    chart = chart.convert("RGBA")
    info_size = 20
    info_font = ImageFont.truetype('minecraft_font.ttf', info_size)

    overlay = Image.new('RGBA', chart.size, (0, 0, 0)+(0,))
    draw = ImageDraw.Draw(overlay)
    opacity = 128

    for box in get_boxes():
        draw.rectangle(box, fill=(0, 0, 0)+(opacity,), outline=(255, 255, 255)+(opacity,), width=5)

    chart = Image.alpha_composite(chart, overlay)

    shaped_image = ImageDraw.Draw(chart)

    for line in get_lines():
        shaped_image.line(line, fill="#cccccc", width=5)

    texts_pos = get_text_pos()
    for i in range(len(texts_pos[0])):
        x = 600 - int(word.calc_length(texts_pos[0][i], info_size) / 2)
        y = texts_pos[1][i] - int(word.horiz_to_vert(info_size) / 2)
        shaped_image.text((x, y), texts_pos[0][i], font=info_font, fill="#ffff00")

    return chart


def get_lines():
    lines = []
    x = 600
    spacing = 30

    top_y = 120
    bottom_y = 1180

    coords = [top_y] + get_text_pos()[1] + [bottom_y]
    for i, coord in enumerate(coords):
        if i != 0:
            lines.append([(x, coords[i-1]+spacing), (x, coord-spacing)])
    return [] # lines


def get_text_pos():
    pos = [300, 500]
    texts = ["vs.", "match splits"]
    return [texts, pos]


def get_boxes():
    boxes = [[200, 150, 950, 270],
             [250, 330, 1000, 450]]

    return boxes
