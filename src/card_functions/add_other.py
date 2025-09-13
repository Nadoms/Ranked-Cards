from datetime import datetime
from os import path

from PIL import Image, ImageDraw, ImageFont

from rankedutils import word


def write(card):
    othered_image = ImageDraw.Draw(card)
    other_font = ImageFont.truetype("minecraft_font.ttf", 20)

    othered_image.text(
        (1700 - word.calc_length(get_date(), 20), 1155),
        get_date(),
        font=other_font,
        fill="yellow",
    )
    othered_image.text(
        (1700 - word.calc_length("Bot created by Nadoms", 20), 1120),
        "Bot created by Nadoms",
        font=other_font,
        fill="white",
    )
    logo = get_logo()
    card.paste(logo, (1680, 978), logo)

    return card


def get_date():
    date = datetime.now().strftime("Generated at %H:%M on %d/%m/%y")
    return date


def get_logo():
    file = path.join("src", "pics", "other", "ranked_logo.webp")
    logo = Image.open(file)
    logo = logo.resize(
        (round(logo.size[0] * 1), round(logo.size[1] * 1)), resample=Image.NEAREST
    )
    return logo
