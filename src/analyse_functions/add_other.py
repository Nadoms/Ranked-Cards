from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from os import path

from gen_functions import word

# rank with a circle indicating how close to the next main rank, with lines for each division

def write(analysis):
    othered_image = ImageDraw.Draw(analysis)
    other_font = ImageFont.truetype('minecraft_font.ttf', 20)

    othered_image.text((1700-word.calc_length(get_date(), 20), 1155), get_date(), font=other_font, fill="yellow")
    othered_image.text((1700-word.calc_length("mcsrranked.com/discord", 20), 1120), "mcsrranked.com/discord", font=other_font, fill="lightblue")
    logo = get_logo()
    analysis.paste(logo, (1680, 978), logo)

    return analysis

def get_date():
    date = datetime.now().strftime("Generated at %H:%M on %d/%m/%y")
    return date

def get_logo():
    file = path.join("src", "pics", "other", "ranked_logo.webp")
    logo = Image.open(file)
    logo = logo.resize((round(logo.size[0]*1), round(logo.size[1]*1)), resample=Image.NEAREST)
    return logo