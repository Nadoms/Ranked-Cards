from PIL import Image, ImageDraw, ImageFont

from gen_functions import word

def write(analysis, names, response):
    analysis = analysis.convert("RGBA") # Remove alpha for saving in jpg format.
    info_size = 20
    info_font = ImageFont.truetype('minecraft_font.ttf', info_size)

    # Make a blank image the same size as the image for the rectangle, initialized
    # to a fully transparent (0% opaque) version of the tint color, then draw a
    # semi-transparent version of the square on it.
    overlay = Image.new('RGBA', analysis.size, (0, 0, 0)+(0,))
    draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
    opacity = 128

    for box in get_boxes(names, response):
        draw.rectangle(box, fill=(0, 0, 0)+(opacity,), outline=(255, 255, 255)+(opacity,), width=5)

    # Alpha composite these two images together to obtain the desired result.
    analysis = Image.alpha_composite(analysis, overlay)
    
    shaped_image = ImageDraw.Draw(analysis)

    for line in get_lines():
        shaped_image.line(line, fill="#cccccc", width=5)

    texts_pos = get_text_pos()
    for i in range(len(texts_pos[0])):
        x = 960 - word.calc_length(texts_pos[0][i], info_size) / 2
        y = texts_pos[1][i] - int(word.horiz_to_vert(info_size) / 2)
        shaped_image.text((x, y), texts_pos[0][i], font=info_font, fill="#ffff00")
    
    return analysis

def get_lines():
    lines = []
    x = 960
    spacing = 30

    top_y = 120
    bottom_y = 1180

    coords = [top_y] + get_text_pos()[1] + [bottom_y]
    for i in range(len(coords)):
        if i != 0:
            lines.append([(x, coords[i-1]+spacing), (x, coords[i]-spacing)])
    return lines

def get_text_pos():
    pos = [210, 370, 440, 510, 580]
    texts = ["vs", "elo then", "elo now", "total gain", "score"]
    return [texts, pos]

def get_boxes(names, response):
    spacing = 140
    left_x = 960 - spacing
    right_x = 960 + spacing
    top_y = 170
    bottom_y = 260
    extra_length = 160
    boxes = [[left_x-word.calc_length(names[0], min(word.calc_size(names[0], 460), 90)) - extra_length, top_y, left_x, bottom_y],
             [right_x, top_y, right_x+word.calc_length(names[1], min(word.calc_size(names[1], 460), 90)) + extra_length, bottom_y],
             [820, 370, 1100, 580]]
    for box in boxes:
        box[0] -= 40
        box[1] -= 30
        box[2] += 40
        box[3] += 30
    return boxes