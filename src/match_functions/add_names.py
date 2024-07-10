from os import path

from PIL import ImageDraw, ImageFont, Image

from gen_functions import word

def write(chart, names, response):
    named_image = ImageDraw.Draw(chart)
    middle = 600
    icon_x_values = [middle-510, middle+510]
    x_values = [middle+50, middle-50]
    y_values = [210, 390]

    for i in range(0, 2):
        rank = str(response["players"][i]["eloRank"])
        rank_colour = get_rank_colour(rank)
        if rank == "None":
            rank = "-"
        rank = " #" + rank
        rank = "" # FIX: remove rank

        tag = names[i] + rank
        tag_size = min(word.calc_size(tag, 500), 75)
        tag_font = ImageFont.truetype('minecraft_font.ttf', tag_size)
        text_x = int(x_values[i] - word.calc_length(tag, tag_size) / 2)
        text_y = int(y_values[i] - word.horiz_to_vert(tag_size) / 2)
        if response["players"][i]["uuid"] == response["result"]["uuid"]:
            colour = "#ffaa00"
        else:
            colour = "lightblue"

        named_image.text((text_x, text_y), names[i], font=tag_font, fill=colour)

        text_x += word.calc_length(names[i], tag_size)+tag_size/5
        named_image.text((text_x, text_y), rank, font=tag_font, fill=rank_colour)

        if response["players"][i]["uuid"] == response["result"]["uuid"]:
            icon_name = "8.webp"
        else:
            icon_name = "10.webp"
        file = path.join("src", "pics", "items", icon_name)
        icon = Image.open(file)
        icon = icon.resize((100, 100))

        icon_x = int(icon_x_values[i] - icon.size[0] / 2)
        icon_y = int(y_values[i] - icon.size[1] / 2)

        chart.paste(icon, (icon_x, icon_y), icon)

    return chart

def get_rank_colour(rank):
    rank_colours = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#0f52ba", "#cd7f32", "#c0c0c0", "#ffd700"]
    if rank != "None":
        rounded_rank = int(rank)
        if rounded_rank > 1000:
            colour_id = 0
        elif rounded_rank > 500:
            colour_id = 1
        elif rounded_rank > 100:
            colour_id = 2
        elif rounded_rank > 10:
            colour_id = 3
        elif rounded_rank > 3:
            colour_id = 4
        elif rounded_rank == 3:
            colour_id = 5
        elif rounded_rank == 2:
            colour_id = 6
        elif rounded_rank == 1:
            colour_id = 7
        else:
            colour_id = 0
    else:
        colour_id = 0
    rank_colour = rank_colours[colour_id]

    return rank_colour
