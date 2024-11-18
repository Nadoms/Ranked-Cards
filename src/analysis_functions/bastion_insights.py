import json
from os import path
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from gen_functions import word, numb, rank

SIDES = 4
INIT_PROP = 1.8
IMG_SIZE_X = 960
IMG_SIZE_Y = 760
MIDDLE = IMG_SIZE_Y / 2
OFFSET_X = (IMG_SIZE_X - IMG_SIZE_Y) / 2
OFFSET_Y = 40
ANGLES = [(i * (2 * math.pi)) / SIDES -
          math.pi / 2 +
          2 * math.pi / SIDES for i in range(SIDES)]
ANGLES.insert(0, ANGLES.pop())


def main(uuid, detailed_matches, elo, season):
    number_bastions, average_bastions, average_deaths = get_avg_bastions(uuid, detailed_matches)
    ranked_bastions = get_ranked_bastions(average_bastions)
    polygon = get_polygon(ranked_bastions)
    polygon = add_text(polygon, average_bastions, ranked_bastions)

    comments = {}
    comments["title"] = f"Bastion Performance in Season {season}"
    comments["description"] = f"{len(detailed_matches)} games were used in analysing your bastions. {get_sample_size(len(detailed_matches))}"
    comments["count"] = get_count(number_bastions)
    comments["best"], comments["worst"] = get_best_worst(ranked_bastions)
    if season != 1:
        comments["player_deaths"], comments["rank_deaths"] = get_death_comments(average_deaths, elo)

    return comments, polygon


def get_avg_bastions(uuid, detailed_matches):
    number_bastions = {
        "bridge": 0, "housing": 0, "stables": 0, "treasure": 0
    }
    time_bastions = {
        "bridge": 0, "housing": 0, "stables": 0, "treasure": 0
    }
    average_bastions = {
        "bridge": 0, "housing": 0, "stables": 0, "treasure": 0
    }
    average_deaths = {
        "bridge": 0, "housing": 0, "stables": 0, "treasure": 0
    }
    bastion_conditions = [
        "nether.obtain_crying_obsidian",
        "nether.loot_bastion",
        "story.form_obsidian",
    ]
    post_bastion = [
        "story.find_fortress",
        "projectelo.timeline.blind_travel",
        "story.follow_ender_eye",
        "story.enter_the_end",
    ]

    for match in detailed_matches:
        if not match["timelines"]:
            continue

        bastion_type = match["bastionType"]
        bastion_entry = 0
        bastion_exit = 0
        found_fortress = False
        bastion_progression = 0

        for event in reversed(match["timelines"]):
            if event["uuid"] != uuid:
                continue

            # If fort first or incomplete bastion route, void the run.
            if (
                (not bastion_entry or bastion_progression < 2)
                and event["type"] in post_bastion
            ):
                break

            # If entering bastion, set entry time.
            elif event["type"] == "story.find_bastion":
                bastion_entry = event["time"]

            elif bastion_entry:
                # If doing bastion things, increase the bastion progression.
                if event["type"] in bastion_conditions:
                    bastion_progression += 1

                # If dying during the bastion, increment the death count.
                elif event["type"] == "projectelo.timeline.death":
                    average_deaths[bastion_type] += 1

                # If resetting, void the rest of the run.
                elif event["type"] == "projectelo.timeline.reset":
                    break

                # If entering fortress after bastion, set the exit time.
                elif event["type"] == "story.find_fortress":
                    bastion_exit = event["time"]

                # If doing some random other split, void the run.
                elif event["type"] in post_bastion:
                    break

            elif event["type"] == "story.find_fortress" and prev_event == "story.find_bastion":
                bastion_length = event["time"] - prev_time
                time_bastions[prev_event] += bastion_length
                number_bastions[prev_event] += 1

                prev_time = event["time"]
                prev_event = event_mapping[event["type"]]

            elif event["type"] == "projectelo.timeline.death":
                average_deaths[] += 1

        if match["result"]["uuid"] == uuid and match["forfeited"] is False:
            bastion_length = match["result"]["time"] - prev_time
            time_bastions[prev_event] += bastion_length
            number_bastions[prev_event] += 1

    for key in average_bastions:
        if number_bastions[key] == 0:
            average_bastions[key] = 1000000000
            average_deaths[key] = 0
        else:
            average_bastions[key] = round(time_bastions[key] / number_bastions[key])
            average_deaths[key] = round(average_deaths[key] / number_bastions[key], 3)

    return number_bastions, average_bastions, average_deaths


def get_ranked_bastions(average_bastions):
    ranked_bastions = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0
    }
    bastions_final_boss = {
        "ow": [],
        "nether": [],
        "bastion": [],
        "fortress": [],
        "blind": [],
        "stronghold": [],
        "end": []
    }

    file = path.join("src", "database", "mcsrstats", "player_bastions.csv")
    bastion_mapping = ["ow", "nether", "bastion", "fortress", "blind", "stronghold", "end"]

    with open(file, "r", encoding="UTF-8") as f:
        while True:
            bastions = f.readline().strip().bastion(",")
            if not bastions[0]:
                break
            for i in range(7):
                if bastions[i] != "FALSE":
                    bastions_final_boss[bastion_mapping[i]].append(int(bastions[i]))

    for key in bastions_final_boss:
        ranked_bastions[key] = np.searchsorted(bastions_final_boss[key], average_bastions[key])
        if len(bastions_final_boss[key]) == 0:
            ranked_bastions[key] = 0
        else:
            ranked_bastions[key] = round(1 - ranked_bastions[key] / len(bastions_final_boss[key]), 3)

    return ranked_bastions


def get_polygon(ranked_bastions):
    proportions = [INIT_PROP, INIT_PROP * 4/3, INIT_PROP * 2, INIT_PROP * 4, 10000]
    bastion_mapping = ["ow", "bastion", "fortress", "blind", "stronghold", "end"]

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
    for i, angle in enumerate(ANGLES):
        val = ranked_bastions[bastion_mapping[i]]
        if val == 0:
            proportion = 100000
        else:
            proportion = INIT_PROP / val
        polygon_size = MIDDLE / proportion
        
        xy.append(
            ((math.cos(angle) + proportion) * polygon_size + OFFSET_X,
            (math.sin(angle) + proportion) * polygon_size + OFFSET_Y)
        )
    stats_draw.polygon(xy, fill="#716388", outline="#a1d3f8", width=4)

    polygon = Image.blend(polygon_frame, polygon_stats, 0.4)

    return polygon


def add_text(polygon, average_bastions, ranked_bastions):
    text_prop = INIT_PROP * 0.95
    xy = []
    percentiles = [0.3, 0.5, 0.7, 0.9, 0.95, 1.0]
    percentile_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#3f82ff", "#ffd700"]
    titles = ["Overworld", "Bastion", "Fortress", "Blind", "Stronghold", "The End"]
    bastion_mapping = ["ow", "bastion", "fortress", "blind", "stronghold", "end"]

    text_draw = ImageDraw.Draw(polygon)
    big_size = 50
    big_font = ImageFont.truetype('minecraft_font.ttf', big_size)
    title_size = 30
    title_font = ImageFont.truetype('minecraft_font.ttf', title_size)
    stat_size = 25
    stat_font = ImageFont.truetype('minecraft_font.ttf', stat_size)

    big_title = "Split Performance"
    big_x = (IMG_SIZE_X - word.calc_length(big_title, big_size)) / 2
    big_y = OFFSET_Y
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
            xy[i][0] += word.calc_length("Strongholdddld", title_size) / 2
            xy[i][1] -= word.horiz_to_vert(title_size) / 2 + word.horiz_to_vert(stat_size) / 2

        elif i == math.ceil(SIDES / 2) and SIDES % 2 == 1:
            xy[i][0] -= word.calc_length("Strongholddldd", title_size) / 8

        elif i == math.floor(SIDES / 2) and SIDES % 2 == 1:
            xy[i][0] += word.calc_length("Strongholddldd", title_size) / 8

        elif math.ceil(SIDES / 2) < i:
            xy[i][0] -= word.calc_length("Strongholddldd", title_size) / 2
            xy[i][1] -= word.horiz_to_vert(title_size) / 2 + word.horiz_to_vert(stat_size) / 2

    for i in range(SIDES):

        s_colour = percentile_colour[0]
        for j in range(len(percentiles)):
            if ranked_bastions[bastion_mapping[i]] <= percentiles[j]:
                s_colour = percentile_colour[j]
                break
        if average_bastions[bastion_mapping[i]] == 1000000000000:
            stat = "No data"
        else:
            time = numb.digital_time(average_bastions[bastion_mapping[i]])
            stat = f"{time} / {word.percentify(ranked_bastions[bastion_mapping[i]])}"

        xy[i][0] -= word.calc_length(titles[i], title_size) / 2
        text_draw.text(xy[i], titles[i], font=title_font, fill="#ffffff", stroke_fill="#000000", stroke_width=2)

        xy[i][0] += word.calc_length(titles[i], title_size) / 2 - word.calc_length(stat, stat_size) / 2
        xy[i][1] += word.horiz_to_vert(title_size)
        text_draw.text(xy[i], stat, font=stat_font, fill=s_colour, stroke_fill="#000000", stroke_width=2)

    return polygon


def get_sample_size(num_games):
    if num_games < 30:
        return "This is a very low sample size. Take these stats with a grain of salt."
    if num_games < 80:
        return "This is an OK sample size."
    else:
        return "This is a large sample size and the data will reflect your bastion skills properly."


def get_count(number_bastions):
    names = " OW  / NTR / BAS / FRT / BLN / SH  / END "
    count = ""
    for bastion in number_bastions:
        num = number_bastions[bastion]
        count += f" {num}"
        count += " " * (4 - len(str(num)))
        if bastion != "end":
            count += "/"
    value = f"`|{names}|`\n`|{count}|`"

    count_comment = {
        "name": "Split Counts",
        "value": value
    }
    return count_comment


def get_best_worst(ranked_bastions):
    bastion_mapping = {
        "ow": "Overworld",
        "nether": "Nether Terrain",
        "bastion": "Bastion",
        "fortress": "Fortress",
        "blind": "Blind",
        "stronghold": "Stronghold",
        "end": "The End"
    }

    best_comments = {
        "ow": "You can handle the variety of overworld very well. Getting ahead early is key!",
        "nether": "You excel at navigating nether terrain and finding structures.",
        "bastion": "Routing bastions is your strongest bastion.",
        "fortress": "Blaze fighting is your strong suit.",
        "blind": "Measuring eyes and nether pearl travel is where you shine.",
        "stronghold": "You are exceptional at finding the portal room quickly.",
        "end": "You're at your best when taking down the ender dragon."
    }
    worst_comments = {
        "ow": "Your overworld routing is slower than your other bastions. Remember to practice every type of overworld!",
        "nether": "Your terrain nav to the bastion is slower than expected. Try to think through all of the different terrain decisions you can make.",
        "bastion": "Your bastion routing is slower than other bastions. There are tons of tools to practice routing, so this is the easiest to improve on!",
        "fortress": "You often falter a little in your fortress bastion. Make sure drop RD for strays on the way to the spawner, and practice your blaze bed.",
        "blind": "You slow down when measuring eyes and pearling to coords. This bastion is often overlooked, so practice it!",
        "stronghold": "Your stronghold nav isn't as fast as your other bastions, make sure to practice premptive - even around mineshafts.",
        "end": "You relax your aggression a bit more when you reach the end. Always go for halfbow or try a zero cycle."
    }

    max_key = ""
    max_val = 0
    min_key = ""
    min_val = 1000000000000000000

    for key in ranked_bastions:
        if ranked_bastions[key] > max_val:
            max_val = ranked_bastions[key]
            max_key = key

        if ranked_bastions[key] < min_val:
            min_val = ranked_bastions[key]
            min_key = key

    best = {
        "name": f"Best Split: {bastion_mapping[max_key]}",
        "value": best_comments[max_key]
    }
    worst = {
        "name": f"Worst Split: {bastion_mapping[min_key]}",
        "value": worst_comments[min_key]
    }

    return [best, worst]


def get_death_comments(average_deaths, elo):
    bastion_mapping = {
        "ow": "Overworld",
        "nether": "Nether Terrain",
        "bastion": "Bastion",
        "fortress": "Fortress",
        "blind": "Blind",
        "stronghold": "Stronghold",
        "end": "The End"
    }
    differences = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0
    }
    ranks = ["Coal", "Iron", "Gold", "Emerald", "Diamond", "Netherite"]

    rank_no = rank.get_rank(elo)
    if rank_no == -1:
        rank_no = 2
    file = path.join("src", "database", "mcsrstats", "deaths", "deaths.json")
    with open (file, "r", encoding="UTF-8") as f:
        overall_deaths = json.load(f)[str(rank_no)]

    max_diff = 0
    max_bastion = None
    for bastion_key in differences:
        differences[bastion_key] = average_deaths[bastion_key] / overall_deaths[bastion_key]
        if differences[bastion_key] > max_diff:
            max_diff = differences[bastion_key]
            max_bastion = bastion_key

    death_comment = {
        "name": "Your Death Rates",
        "value": [f"`{numb.round_sf(average_deaths[bastion] * 100, 3)}%` - {bastion_mapping[bastion]}" for bastion in average_deaths]
    }
    rank_comment = {
        "name": f"Death Rates in {ranks[rank_no]} Elo",
        "value": [f"`{numb.round_sf(overall_deaths[bastion] * 100, 3)}%` - {bastion_mapping[bastion]}" for bastion in overall_deaths]
    }
    return death_comment, rank_comment
