from os import path
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from gen_functions import numb, word

SIDES = 5
INIT_PROP = 1.8
IMG_SIZE_X = 960
IMG_SIZE_Y = 760
MIDDLE = IMG_SIZE_Y / 2
OFFSET_X = (IMG_SIZE_X - IMG_SIZE_Y) / 2
OFFSET_Y = 60
ANGLES = [(i * (2 * math.pi)) / SIDES -
          math.pi / 2 +
          2 * math.pi / SIDES for i in range(SIDES)]
ANGLES.insert(0, ANGLES.pop())


def main(uuid, detailed_matches, season):
    number_ows, average_ows = get_avg_ows(uuid, detailed_matches)
    ranked_ows = get_ranked_ows(average_ows)
    polygon = get_polygon(ranked_ows)
    polygon = add_text(polygon, average_ows, ranked_ows)

    comments = {}
    comments["title"] = f"Overworld Performance in Season {season}"
    comments["description"] = f"{len(detailed_matches)} games were used in analysing your overworlds. {get_sample_size(len(detailed_matches))}"
    comments["count"] = get_count(number_ows)
    comments["best"], comments["worst"] = get_best_worst(ranked_ows)

    return comments, polygon


def get_avg_ows(uuid, detailed_matches):
    number_ows = {
        "bt": 0, "dt": 0, "rp": 0, "ship": 0, "village": 0
    }
    time_ows = {
        "bt": 0, "dt": 0, "rp": 0, "ship": 0, "village": 0
    }
    average_ows = {
        "bt": 0, "dt": 0, "rp": 0, "ship": 0, "village": 0
    }
    ow_mapping = {
        "BURIED_TREASURE": "bt",
        "DESERT_TEMPLE": "dt",
        "RUINED_PORTAL": "rp",
        "SHIPWRECK": "ship",
        "VILLAGE": "village"
    }

    for match in detailed_matches:
        if not match["timelines"]:
            continue

        seed_type = match["seedType"]

        for event in reversed(match["timelines"]):
            if event["uuid"] != uuid:
                continue

            if event["type"] == "story.enter_the_nether":
                time_ows[ow_mapping[seed_type]] += event["time"]
                number_ows[ow_mapping[seed_type]] += 1
                break

    for ow_key in average_ows:
        if number_ows[ow_key] == 0:
            average_ows[ow_key] = 1000000000000
        else:
            average_ows[ow_key] = round(time_ows[ow_key] / number_ows[ow_key])

    return number_ows, average_ows


def get_ranked_ows(average_ows):
    ranked_ows = {
        "bt": 0, "dt": 0, "rp": 0, "ship": 0, "village": 0
    }
    ows_final_boss = {
        "bt": [], "dt": [], "rp": [], "ship": [], "village": []
    }

    file = path.join("src", "database", "mcsrstats", "ow_splits.csv")
    ows_index = ["bt", "dt", "rp", "ship", "village"]
    
    with open(file, "r", encoding="UTF-8") as f:
        while True:
            ows = f.readline().strip().split(",")
            if not ows[0]:
                break
            for i in range(5):
                if ows[i] != "FALSE":
                    ows_final_boss[ows_index[i]].append(int(ows[i]))

    for ow_key in ows_final_boss:
        ranked_ows[ow_key] = np.searchsorted(ows_final_boss[ow_key], average_ows[ow_key])
        if len(ows_final_boss[ow_key]) == 0:
            ranked_ows[ow_key] = 0
        else:
            ranked_ows[ow_key] = round(1 - ranked_ows[ow_key] / len(ows_final_boss[ow_key]), 3)

    return ranked_ows


def get_polygon(ranked_ows):
    proportions = [INIT_PROP, INIT_PROP * 4/3, INIT_PROP * 2, INIT_PROP * 4, 10000]
    ow_mapping = ["bt", "dt", "rp", "ship", "village"]

    polygon_frame = Image.new('RGBA', (IMG_SIZE_X, IMG_SIZE_Y), (0, 0, 0, 0))
    frame_draw = ImageDraw.Draw(polygon_frame)

    # Filling the polygon
    polygon_size = MIDDLE / INIT_PROP
    xy = [
        ((math.cos(th) + INIT_PROP) * polygon_size + OFFSET_X, 
        (math.sin(th) + INIT_PROP) * polygon_size + OFFSET_Y) 
        for th in ANGLES
    ]
    frame_draw.polygon(xy, fill="#413348")

    # Drawing the outward lines of the polygon
    for th in ANGLES:
        polygon_size = MIDDLE / INIT_PROP
        # th = (i * (2 * math.pi) - 0.5 * math.pi) / SIDES
        xy = [(MIDDLE + OFFSET_X, MIDDLE + OFFSET_Y),
            ((math.cos(th) + INIT_PROP) * polygon_size + OFFSET_X, 
            (math.sin(th) + INIT_PROP) * polygon_size + OFFSET_Y)
        ]
        frame_draw.line(xy, fill="#515368", width=3)

    # Drawing the edge of the polygons
    for proportion in proportions:
        polygon_size = MIDDLE / proportion
        xy = [ 
            ((math.cos(th) + proportion) * polygon_size + OFFSET_X, 
            (math.sin(th) + proportion) * polygon_size + OFFSET_Y) 
            for th in ANGLES 
        ]
        if proportion == INIT_PROP:
            frame_draw.polygon(xy, outline="#ffffff", width=6)
        else:
            frame_draw.polygon(xy, outline="#515368", width=3)

    polygon_stats = polygon_frame.copy()
    stats_draw = ImageDraw.Draw(polygon_frame)

    # Drawing the player's polygon
    xy = []
    for i in range(len(ANGLES)):
        val = ranked_ows[ow_mapping[i]]
        if val == 0:
            proportion = 100000
        else:
            proportion = INIT_PROP / val
        polygon_size = MIDDLE / proportion
        
        xy.append(
            ((math.cos(ANGLES[i]) + proportion) * polygon_size + OFFSET_X,
            (math.sin(ANGLES[i]) + proportion) * polygon_size + OFFSET_Y)
        )
    stats_draw.polygon(xy, fill="#716388", outline="#a1d3f8", width=4)

    polygon = Image.blend(polygon_frame, polygon_stats, 0.4)

    return polygon


def add_text(polygon, average_ows, ranked_ows):
    text_prop = INIT_PROP * 0.95
    xy = []
    percentiles = [0.3, 0.5, 0.7, 0.9, 0.95, 1.0]
    percentile_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#3f82ff", "#ffd700"]
    titles = ["Buried Treasure", "Temple", "Ruined Portal", "Shipwreck", "Village"]
    ow_mapping = ["bt", "dt", "rp", "ship", "village"]

    text_draw = ImageDraw.Draw(polygon)
    big_size = 50
    big_font = ImageFont.truetype('minecraft_font.ttf', big_size)
    title_size = 30
    title_font = ImageFont.truetype('minecraft_font.ttf', title_size)
    stat_size = 25
    stat_font = ImageFont.truetype('minecraft_font.ttf', stat_size)

    big_title = "Overworld Performance"
    big_x = (IMG_SIZE_X - word.calc_length(big_title, big_size)) / 2
    big_y = OFFSET_Y - 20
    text_draw.text((big_x, big_y), big_title, font=big_font, fill="#ffffff", stroke_fill="#000000", stroke_width=3)

    for angle in ANGLES:
        polygon_size = MIDDLE / text_prop
        xy.append(
            [(math.cos(angle) + text_prop) * polygon_size + OFFSET_X,
            (math.sin(angle) + text_prop) * polygon_size + OFFSET_Y]
        )

    for i in range(SIDES):
        if i == 0:
            xy[i][1] -= word.horiz_to_vert(title_size) + word.horiz_to_vert(stat_size)

        elif i < math.floor(SIDES / 2):
            xy[i][0] += word.calc_length("Strongholdddl", title_size) / 2
            xy[i][1] -= word.horiz_to_vert(title_size) / 2 + word.horiz_to_vert(stat_size) / 2

        elif i == math.ceil(SIDES / 2) and SIDES % 2 == 1:
            xy[i][0] -= word.calc_length("Strongholdddl", title_size) / 8

        elif i == math.floor(SIDES / 2) and SIDES % 2 == 1:
            xy[i][0] += word.calc_length("Strongholdddl", title_size) / 8

        elif math.ceil(SIDES / 2) < i:
            xy[i][0] -= word.calc_length("Strongholdddl", title_size) / 2
            xy[i][1] -= word.horiz_to_vert(title_size) / 2 + word.horiz_to_vert(stat_size) / 2

    for i in range(SIDES):

        s_colour = percentile_colour[0]
        for j in range(len(percentiles)):
            if ranked_ows[ow_mapping[i]] <= percentiles[j]:
                s_colour = percentile_colour[j]
                break
        if average_ows[ow_mapping[i]] == 1000000000000:
            stat = "No data"
        else:
            time = numb.digital_time(average_ows[ow_mapping[i]])
            stat = f"{time} / {word.percentify(ranked_ows[ow_mapping[i]])}"

        xy[i][0] -= word.calc_length(titles[i], title_size) / 2
        text_draw.text(xy[i], titles[i], font=title_font, fill="#ffffff", stroke_fill="#000000", stroke_width=2)

        xy[i][0] += word.calc_length(titles[i], title_size) / 2 - word.calc_length(stat, stat_size) / 2
        xy[i][1] += word.horiz_to_vert(title_size)
        text_draw.text(xy[i], stat, font=stat_font, fill=s_colour, stroke_fill="#000000", stroke_width=2)

    return polygon


def get_sample_size(num_games):
    if num_games < 30:
        return "This is a very low sample size. Take the RP and DT averages with a grain of salt."
    if num_games < 80:
        return "This is an OK sample size."
    else:
        return "This is a large sample size and the data will reflect your overworld skills properly."


def get_count(number_ows):
    names = " BT  / DT  / RP  / SHP / VIL "
    count = ""
    for ow in number_ows:
        num = number_ows[ow]
        count += f" {num}"
        count += " " * (4 - len(str(num)))
        if ow != "village":
            count += "/"
    value = f"`|{names}|`\n`|{count}|`"

    count_comment = {
        "name": "Overworld Counts",
        "value": value,
        "inline": False,
    }
    return count_comment


def get_best_worst(ranked_ows):
    ow_mapping = {
        "bt": "Buried Treasure",
        "dt": "Desert Temple",
        "rp": "Ruined Portal",
        "ship": "Shipwreck",
        "village": "Village"
    }
    # best_comments = {
    #     "bt": "You're most comfortable with mapless, island crafts and magma portals.",
    #     "dt": "You're fastest with routing the overworlds of desert temples.",
    #     "rp": "You excel at finding and looting ruined portals, as well as foraging around them.",
    #     "ship": "You're at your best when spotting shipwrecks and magma ravines.",
    #     "village": "Routing villages is your strongest overworld ability."
    # }
    # worst_comments = {
    #     "bt": "You're slower at finding buried treasures than expected. Practice finding the correct chunk with only 2 pie chart swipes!",
    #     "dt": "Your desert temple overworlds are slower than others. Make sure to take mental notes of what's around you as you move.",
    #     "rp": "You falter with ruined portal overworlds. Make sure to think ahead about what you're crafting while getting wood or food.",
    #     "ship": "Your shipwrecks aren't as fast as your other overworlds. Remember that you can use mapless for these too!",
    #     "village": "Routing villages is where you slow down the most. Plan out movements in advance as you go from the blacksmith, to hay, to the golem."
    # }

    max_key = ""
    max_val = -1
    min_key = ""
    min_val = 1000000000000000000

    for key in ranked_ows:
        if ranked_ows[key] > max_val:
            max_val = ranked_ows[key]
            max_key = key

        if ranked_ows[key] < min_val:
            min_val = ranked_ows[key]
            min_key = key

    best = {
        "name": "Strongest Overworld Type",
        "value": f"`{word.percentify(ranked_ows[max_key])}` - {ow_mapping[max_key]}",
        "inline": True,
    }
    worst = {
        "name": f"Weakest Overworld Type",
        "value": f"`{word.percentify(ranked_ows[min_key])}` - {ow_mapping[min_key]}",
        "inline": True,
    }

    return [best, worst]
