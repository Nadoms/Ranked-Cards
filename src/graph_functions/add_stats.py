from PIL import ImageDraw, ImageFont

from gen_functions import word, rank

def write(graph, response):
    statted_image = ImageDraw.Draw(graph)
    stat_size = 20
    stat_font = ImageFont.truetype('minecraft_font.ttf', stat_size)
    rank_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#0f52ba", "#cd7f32", "#c0c0c0", "#ffd700"]
    white = "#ffffff"

    stats = get_stats(response)
    colour = rank.get_colour(stats[1])

    if stats[1] is None:
        stats[1] = "-"
    else:
        stats[1] = str(stats[1])
    if stats[3] is not None:
        rounded_rank = int(stats[3])
        if rounded_rank > 1000:
            rounded_rank = 0
        elif rounded_rank > 500:
            rounded_rank = 1
        elif rounded_rank > 100:
            rounded_rank = 2
        elif rounded_rank > 10:
            rounded_rank = 3
        elif rounded_rank > 3:
            rounded_rank = 4
        elif rounded_rank == 3:
            rounded_rank = 5
        elif rounded_rank == 2:
            rounded_rank = 6
        elif rounded_rank == 1:
            rounded_rank = 7
        else:
            rounded_rank = 0
    else:
        stats[3] = "-"
        rounded_rank = 0
    stats[3] = "#" + str(stats[3])

    x = 125
    statted_image.text((x, 60), stats[0], font=stat_font, fill=white)
    x += word.calc_length(stats[0], stat_size)
    statted_image.text((x, 60), stats[1], font=stat_font, fill=colour[0], stroke_fill=colour[1], stroke_width=1)
    x += word.calc_length(stats[1], stat_size)
    statted_image.text((x, 60), stats[2], font=stat_font, fill=white)
    x += word.calc_length(stats[2], stat_size)
    statted_image.text((x, 60), stats[3], font=stat_font, fill=rank_colour[rounded_rank])

    return graph

def get_stats(response):
    elo = response["eloRate"]
    ranking = response["eloRank"]

    return ["Current Elo: ", elo, " / Rank: ", ranking]
