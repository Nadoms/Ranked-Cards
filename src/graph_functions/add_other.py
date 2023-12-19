from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from os import path

from gen_functions import word

# rank with a circle indicating how close to the next main rank, with lines for each division

def write(graph):
    othered_image = ImageDraw.Draw(graph)
    other_font = ImageFont.truetype('minecraft_font.ttf', 12)

    othered_image.text((795-word.calc_length(get_date(), 12), 5), get_date(), font=other_font, fill="yellow")
    othered_image.text((795-word.calc_length("mcsrranked.com/discord", 12), 25), "mcsrranked.com/discord", font=other_font, fill="lightblue")
    logo = get_logo()
    graph.paste(logo, (725, 35), logo)

    return graph

def get_date():
    date = datetime.now().strftime("Generated at %H:%M on %d/%m/%y")
    return date

def get_logo():
    file = path.join("src", "pics", "other", "ranked_logo.webp")
    logo = Image.open(file)
    logo = logo.resize((round(logo.size[0]*0.3), round(logo.size[1]*0.3)), resample=Image.NEAREST)
    return logo