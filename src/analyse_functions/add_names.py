from PIL import ImageDraw
from PIL import ImageFont

from gen_functions import word

def write(analysis, names, response):
    named_image = ImageDraw.Draw(analysis)
    x_values = [650, 1270]

    for i in range(0, 2):
        rank = str(response["members"][i]["eloRank"])
        rank_colour = get_rank_colour(rank)
        if rank == "None":
            rank = "-"
        rank = " #" + rank

        tag = names[i] + rank
        tag_size = min(word.calc_size(tag, 590), 100)
        tag_font = ImageFont.truetype('minecraft_font.ttf', tag_size)
        x = int(x_values[i] + (i-1) * word.calc_length(tag, tag_size))
        y = 120 - int(word.horiz_to_vert(tag_size) / 2)
        
        named_image.text((x, y), names[i], font=tag_font, fill="#ffffff")

        x += word.calc_length(names[i], tag_size)+tag_size/5
        named_image.text((x, y), rank, font=tag_font, fill=rank_colour)
    return analysis

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