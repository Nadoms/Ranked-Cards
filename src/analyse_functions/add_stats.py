from PIL import ImageDraw, ImageFont
import requests
from datetime import timedelta

from gen_functions import word, rank, match

def write(analysis, uuids, response, vs_response):
    statted_image = ImageDraw.Draw(analysis)
    stat_size = 30
    stat_font = ImageFont.truetype('minecraft_font.ttf', stat_size)
    x_values = [900, 1020]
    y_values = [250, 320, 390]

    scores = get_scores(uuids, vs_response)

    for i in range(0, 2):
        stats = get_stats(response["members"][i]) + [scores[i]]
        elo_colour = rank.get_colour(int(stats[0]))[0]
        rank_colour = get_rank_colour(stats[i])
        score_colour = "#00ffff"
        colours = [elo_colour, rank_colour, score_colour]

        stats[1] = "#" + stats[1]

        for j in range(len(stats)):
            x = int(x_values[i] + (i-1) * word.calc_length(stats[j], stat_size))
            y = y_values[j] - int(word.horiz_to_vert(stat_size) / 2)

            statted_image.text((x, y), stats[j], font=stat_font, fill=colours[j])
        
    return analysis

def get_stats(response):
    elo = str(response["elo_rate"])
    rank = str(response["elo_rank"])

    return [elo, rank]

def get_scores(uuids, vs_response):
    scores = []
    for uuid in uuids:
        score = 0
        for season in vs_response["win_count"]:
            score += vs_response["win_count"][season][uuid]
        scores.append(str(score))

    return scores

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
        rank = "-"
        colour_id = 0
    rank_colour = rank_colours[colour_id]

    return rank_colour