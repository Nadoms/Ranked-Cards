import json
from os import path
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from gen_functions import word, numb, rank
from analysis_functions.bastion_insights import add_rank_img

SIDES = 7
INIT_PROP = 1.8
IMG_SIZE_X = 960
IMG_SIZE_Y = 760
MIDDLE = IMG_SIZE_Y / 2
OFFSET_X = (IMG_SIZE_X - IMG_SIZE_Y) / 2
OFFSET_Y = 40
ANGLES = [
    (i * (2 * math.pi)) / SIDES - math.pi / 2 + 2 * math.pi / SIDES
    for i in range(SIDES)
]
ANGLES.insert(0, ANGLES.pop())


def main(uuid, detailed_matches, elo, season, num_comps, rank_filter):
    number_splits, average_splits, average_deaths = get_avg_splits(
        uuid, detailed_matches
    )
    ranked_splits = get_ranked_splits(average_splits, rank_filter)
    polygon = get_polygon(ranked_splits)
    polygon = add_text(polygon, average_splits, ranked_splits, rank_filter)

    comments = {}
    comments["title"] = f"Split Performance"
    comments["description"] = (
        f"{len(detailed_matches)} games (with {num_comps} completions) were used in analysing your splits. {get_sample_size(num_comps)}"
    )
    comments["count"] = get_count(number_splits)
    comments["best"], comments["worst"] = get_best_worst(ranked_splits)
    if season != 1:
        comments["player_deaths"], comments["rank_deaths"] = get_death_comments(
            average_deaths, elo, rank_filter
        )

    return comments, polygon


def get_avg_splits(uuid, detailed_matches):
    number_splits = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0,
    }
    time_splits = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0,
    }
    average_splits = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0,
    }
    average_deaths = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0,
    }
    death_opportunities = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0,
    }
    event_mapping = {
        "story.enter_the_nether": "nether",
        "nether.find_bastion": "bastion",
        "nether.find_fortress": "fortress",
        "projectelo.timeline.blind_travel": "blind",
        "story.follow_ender_eye": "stronghold",
        "story.enter_the_end": "end",
    }

    for match in detailed_matches:
        if not match["timelines"]:
            continue

        prev_event = "ow"
        prev_time = 0
        death_opportunities["ow"] += 1

        for event in reversed(match["timelines"]):
            if event["uuid"] != uuid:
                continue

            if event["type"] == "projectelo.timeline.reset":
                prev_time = event["time"]
                prev_event = "ow"
                death_opportunities[prev_event] += 1

            elif event["type"] in event_mapping:
                split_length = event["time"] - prev_time
                time_splits[prev_event] += split_length
                number_splits[prev_event] += 1

                prev_time = event["time"]
                prev_event = event_mapping[event["type"]]
                death_opportunities[prev_event] += 1

            elif event["type"] == "projectelo.timeline.death":
                average_deaths[prev_event] += 1

        # If the opponent ended the game, discount the split as an opportunity to die.
        else:
            if (
                match["result"]["uuid"] != uuid and not match["forfeited"]
                and match["result"]["uuid"] == uuid and match["forfeited"]
            ):
                death_opportunities[prev_event] -= 1

        if match["result"]["uuid"] == uuid and match["forfeited"] is False:
            split_length = match["result"]["time"] - prev_time
            time_splits[prev_event] += split_length
            number_splits[prev_event] += 1

    for key in average_splits:
        if number_splits[key] == 0:
            average_splits[key] = 1000000000000
            if death_opportunities[key] == 0:
                average_deaths[key] = 0
        else:
            average_splits[key] = round(time_splits[key] / number_splits[key])
            average_deaths[key] = round(average_deaths[key] / death_opportunities[key], 3)

    return number_splits, average_splits, average_deaths


def get_ranked_splits(average_splits, rank_filter):
    ranked_splits = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0,
    }
    splits_final_boss = {
        "ow": [],
        "nether": [],
        "bastion": [],
        "fortress": [],
        "blind": [],
        "stronghold": [],
        "end": [],
    }

    playerbase_file = Path("src") / "database" / "playerbase.json"
    with open(playerbase_file, "r") as f:
        splits_final_boss = json.load(f)["split"]

    lower, upper = rank.get_boundaries(rank_filter)

    for key in splits_final_boss:
        splits_sample = [
            attr[0]
            for attr in splits_final_boss[key]
            if rank_filter is None or (attr[1] and lower <= attr[1] < upper)
        ]
        ranked_splits[key] = np.searchsorted(
            splits_sample,
            average_splits[key],
        )
        if len(splits_sample) == 0:
            ranked_splits[key] = 0
        else:
            ranked_splits[key] = round(
                1 - ranked_splits[key] / len(splits_sample), 3
            )

    return ranked_splits


def get_polygon(ranked_splits):
    proportions = [INIT_PROP, INIT_PROP * 4 / 3, INIT_PROP * 2, INIT_PROP * 4, 10000]
    split_mapping = ["ow", "nether", "bastion", "fortress", "blind", "stronghold", "end"]

    polygon_frame = Image.new("RGBA", (IMG_SIZE_X, IMG_SIZE_Y), (0, 0, 0, 0))
    frame_draw = ImageDraw.Draw(polygon_frame)

    # Filling the polygon
    polygon_size = MIDDLE / INIT_PROP
    xy = [
        (
            (math.cos(th) + INIT_PROP) * polygon_size + OFFSET_X,
            (math.sin(th) + INIT_PROP) * polygon_size + OFFSET_Y,
        )
        for th in ANGLES
    ]
    frame_draw.polygon(xy, fill="#413348")

    # Drawing the outward lines of the polygon
    for th in ANGLES:
        polygon_size = MIDDLE / INIT_PROP
        # th = (i * (2 * math.pi) - 0.5 * math.pi) / SIDES
        xy = [
            (MIDDLE + OFFSET_X, MIDDLE + OFFSET_Y),
            (
                (math.cos(th) + INIT_PROP) * polygon_size + OFFSET_X,
                (math.sin(th) + INIT_PROP) * polygon_size + OFFSET_Y,
            ),
        ]
        frame_draw.line(xy, fill="#515368", width=3)

    # Drawing the edge of the polygons
    for proportion in proportions:
        polygon_size = MIDDLE / proportion
        xy = [
            (
                (math.cos(th) + proportion) * polygon_size + OFFSET_X,
                (math.sin(th) + proportion) * polygon_size + OFFSET_Y,
            )
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
        val = ranked_splits[split_mapping[i]]
        if val == 0:
            proportion = 100000
        else:
            proportion = INIT_PROP / val
        polygon_size = MIDDLE / proportion

        xy.append(
            (
                (math.cos(angle) + proportion) * polygon_size + OFFSET_X,
                (math.sin(angle) + proportion) * polygon_size + OFFSET_Y,
            )
        )
    stats_draw.polygon(xy, fill="#716388", outline="#a1d3f8", width=4)

    polygon = Image.blend(polygon_frame, polygon_stats, 0.4)

    return polygon


def add_text(polygon, average_splits, ranked_splits, rank_filter):
    text_prop = INIT_PROP * 0.95
    xy = []
    percentiles = [0.3, 0.5, 0.7, 0.9, 0.95, 1.0]
    percentile_colour = [
        "#888888",
        "#b3c4c9",
        "#86b8db",
        "#50fe50",
        "#3f82ff",
        "#ffd700",
    ]
    titles = ["Overworld", "Nether", "Bastion", "Fortress", "Blind", "Stronghold", "The End"]
    split_mapping = ["ow", "nether", "bastion", "fortress", "blind", "stronghold", "end"]

    big_size = 50
    big_font = ImageFont.truetype("minecraft_font.ttf", big_size)
    title_size = 30
    title_font = ImageFont.truetype("minecraft_font.ttf", title_size)
    stat_size = 25
    stat_font = ImageFont.truetype("minecraft_font.ttf", stat_size)

    big_title = "Split Performance"
    big_x = int((IMG_SIZE_X - word.calc_length(big_title, big_size)) / 2)
    big_y = OFFSET_Y

    if rank_filter is not None:
        polygon = add_rank_img(polygon, rank_filter, (big_x, big_y), big_size)

    text_draw = ImageDraw.Draw(polygon)
    text_draw.text(
        (big_x, big_y),
        big_title,
        font=big_font,
        fill="#ffffff",
        stroke_fill="#000000",
        stroke_width=3,
    )

    for angle in ANGLES:
        polygon_size = MIDDLE / text_prop
        xy.append(
            [
                (math.cos(angle) + text_prop) * polygon_size + OFFSET_X,
                (math.sin(angle) + text_prop) * polygon_size + OFFSET_Y,
            ]
        )

    for i in range(SIDES):
        if i == 0:
            xy[i][1] -= word.horiz_to_vert(title_size) + word.horiz_to_vert(stat_size)

        elif i < math.floor(SIDES / 2):
            xy[i][0] += word.calc_length("Strongholdddld", title_size) / 2
            xy[i][1] -= (
                word.horiz_to_vert(title_size) / 2 + word.horiz_to_vert(stat_size) / 2
            )

        elif i == math.ceil(SIDES / 2) and SIDES % 2 == 1:
            xy[i][0] -= word.calc_length("Strongholddld", title_size) / 8

        elif i == math.floor(SIDES / 2) and SIDES % 2 == 1:
            xy[i][0] += word.calc_length("Strongholddld", title_size) / 8

        elif math.ceil(SIDES / 2) < i:
            xy[i][0] -= word.calc_length("Strongholddld", title_size) / 2
            xy[i][1] -= (
                word.horiz_to_vert(title_size) / 2 + word.horiz_to_vert(stat_size) / 2
            )

    for i in range(SIDES):

        s_colour = percentile_colour[0]
        for j in range(len(percentiles)):
            if ranked_splits[split_mapping[i]] <= percentiles[j]:
                s_colour = percentile_colour[j]
                break
        if average_splits[split_mapping[i]] == 1000000000000:
            stat = "No data"
        else:
            time = numb.digital_time(average_splits[split_mapping[i]])
            stat = f"{time} / {word.percentify(ranked_splits[split_mapping[i]])}"

        xy[i][0] -= word.calc_length(titles[i], title_size) / 2
        text_draw.text(
            xy[i],
            titles[i],
            font=title_font,
            fill="#ffffff",
            stroke_fill="#000000",
            stroke_width=2,
        )

        xy[i][0] += (
            word.calc_length(titles[i], title_size) / 2
            - word.calc_length(stat, stat_size) / 2
        )
        xy[i][1] += word.horiz_to_vert(title_size)
        text_draw.text(
            xy[i],
            stat,
            font=stat_font,
            fill=s_colour,
            stroke_fill="#000000",
            stroke_width=2,
        )

    return polygon


def get_sample_size(num_comps):
    if num_comps < 8:
        return (
            "This is a very low sample size. Your lategame averages won't be reliable."
        )
    if num_comps < 20:
        return "This is an OK sample size."
    else:
        return "This is a large sample size and the data will reflect your skill across each split properly."


def get_count(number_splits):
    names = " OW  / NTR / BAS / FRT / BLN / SH  / END "
    count = ""
    for split in number_splits:
        num = number_splits[split]
        count += f" {num}"
        count += " " * (4 - len(str(num)))
        if split != "end":
            count += "/"
    value = f"`|{names}|`\n`|{count}|`"

    count_comment = {
        "name": "Split Counts",
        "value": value,
        "inline": False,
    }
    return count_comment


def get_best_worst(ranked_splits):
    split_mapping = {
        "ow": "Overworld",
        "nether": "Nether Terrain",
        "bastion": "Bastion",
        "fortress": "Fortress",
        "blind": "Blind",
        "stronghold": "Stronghold",
        "end": "The End",
    }

    # best_comments = {
    #     "ow": "You can handle the variety of overworld very well. Getting ahead early is key!",
    #     "nether": "You excel at navigating nether terrain and finding structures.",
    #     "bastion": "Routing bastions is your strongest split.",
    #     "fortress": "Blaze fighting is your strong suit.",
    #     "blind": "Measuring eyes and nether pearl travel is where you shine.",
    #     "stronghold": "You are exceptional at finding the portal room quickly.",
    #     "end": "You're at your best when taking down the ender dragon."
    # }
    # worst_comments = {
    #     "ow": "Your overworld routing is slower than your other splits. Remember to practice every type of overworld!",
    #     "nether": "Your terrain nav to the bastion is slower than expected. Try to think through all of the different terrain decisions you can make.",
    #     "bastion": "Your bastion routing is slower than other splits. There are tons of tools to practice routing, so this is the easiest to improve on!",
    #     "fortress": "You often falter a little in your fortress split. Make sure drop RD for strays on the way to the spawner, and practice your blaze bed.",
    #     "blind": "You slow down when measuring eyes and pearling to coords. This split is often overlooked, so practice it!",
    #     "stronghold": "Your stronghold nav isn't as fast as your other splits, make sure to practice premptive - even around mineshafts.",
    #     "end": "You relax your aggression a bit more when you reach the end. Always go for halfbow or try a zero cycle."
    # }

    max_key = ""
    max_val = -1
    min_key = ""
    min_val = 1000000000000000000

    for key in ranked_splits:
        if ranked_splits[key] > max_val:
            max_val = ranked_splits[key]
            max_key = key

        if ranked_splits[key] < min_val:
            min_val = ranked_splits[key]
            min_key = key

    best = {
        "name": "Strongest Split",
        "value": f"`{word.percentify(ranked_splits[max_key])}` - {split_mapping[max_key]}",
        "inline": True,
    }
    worst = {
        "name": f"Weakest Split",
        "value": f"`{word.percentify(ranked_splits[min_key])}` - {split_mapping[min_key]}",
        "inline": True,
    }

    return [best, worst]


def get_death_comments(average_deaths, elo, rank_filter):
    split_mapping = {
        "ow": "Overworld",
        "nether": "Nether Terrain",
        "bastion": "Bastion",
        "fortress": "Fortress",
        "blind": "Blind",
        "stronghold": "Stronghold",
        "end": "The End",
    }
    differences = {
        "ow": 0,
        "nether": 0,
        "bastion": 0,
        "fortress": 0,
        "blind": 0,
        "stronghold": 0,
        "end": 0,
    }

    if rank_filter is None:
        player_rank = rank.get_rank(elo)
        if player_rank == rank.Rank.UNRANKED:
            player_rank = rank.Rank.GOLD
    else:
        player_rank = rank_filter
    file = path.join("src", "database", "deaths.json")
    with open(file, "r", encoding="UTF-8") as f:
        overall_deaths = json.load(f)["splits"][str(player_rank.value)]

    max_diff = 0
    max_split = None
    for split_key in differences:
        differences[split_key] = average_deaths[split_key] / overall_deaths[split_key]
        if differences[split_key] > max_diff:
            max_diff = differences[split_key]
            max_split = split_key

    death_comment = {
        "name": "Your Death Rates",
        "value": [
            (
                f"`{' ' if average_deaths[split] < 0.1 else ''}"
                f"{numb.round_sf(average_deaths[split] * 100, 3)}%` - {split_mapping[split]}"
            )
            for split in average_deaths
        ],
        "inline": True,
    }
    rank_comment = {
        "name": f"{player_rank} Death Rates",
        "value": [
            (
                f"`{' ' if overall_deaths[split] < 0.1 else ''}"
                f"{numb.round_sf(overall_deaths[split] * 100, 3)}%` - {split_mapping[split]}"
            )
            for split in overall_deaths
        ],
        "inline": True,
    }
    return death_comment, rank_comment
