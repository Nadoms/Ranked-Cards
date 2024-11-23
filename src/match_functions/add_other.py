from datetime import datetime
from os import path

from PIL import Image, ImageDraw, ImageFont

from gen_functions import word

# rank with a circle indicating how close to the next main rank, with lines for each division


def write(chart):
    othered_image = ImageDraw.Draw(chart)
    other_size = 25
    other_font = ImageFont.truetype("minecraft_font.ttf", other_size)

    middle = 600
    x_values = [middle - 70, middle + 70]
    y = 1900

    text_y = y - word.horiz_to_vert(other_size)
    othered_image.text(
        (x_values[0] - word.calc_length("mcsrranked.com/discord", other_size), text_y),
        "mcsrranked.com/discord",
        font=other_font,
        fill="yellow",
    )
    othered_image.text(
        (x_values[1], text_y),
        "Bot created by Nadoms :3",
        font=other_font,
        fill="lightblue",
    )

    logo = get_logo()
    logo_x = int(middle - logo.size[0] / 2)
    logo_y = 1920 - logo.size[1]
    chart.paste(logo, (logo_x, logo_y), logo)

    return chart


def get_date():
    date = datetime.now().strftime("Generated at %H:%M on %d/%m/%y")
    return date


def get_logo():
    file = path.join("src", "pics", "other", "ranked_logo.webp")
    logo = Image.open(file)
    logo = logo.resize((100, 100), resample=Image.NEAREST)
    return logo
