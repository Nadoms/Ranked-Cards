from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime

from . import word

# rank with a circle indicating how close to the next main rank, with lines for each division

def write(card, name):
    othered_image = ImageDraw.Draw(card)
    other_font = ImageFont.truetype('minecraft_font.ttf', 20)

    othered_image.text((1700-word.calc_length(get_date(), 20), 1155), get_date(), font=other_font, fill="yellow")
    othered_image.text((1700-word.calc_length("discord.gg/nnjUSyDErj", 20), 1120), "discord.gg/nnjUSyDErj", font=other_font, fill="lightblue")
    logo = get_logo()
    card.paste(logo, (1680, 978), logo)

    return card

def get_date():
    date = datetime.now().strftime("Generated at %H:%M on %d/%m/%y")
    return date

def get_logo():
    logo = Image.open(fr"src\pics\other\ranked_logo.webp")
    logo = logo.resize((round(logo.size[0]*1), round(logo.size[1]*1)), resample=Image.NEAREST)
    return logo