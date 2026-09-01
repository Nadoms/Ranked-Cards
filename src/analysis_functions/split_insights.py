import json
from os import path
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from rankedutils import constants, word, numb, rank
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
SPLIT_NAMING = {
    "ow": "Overworld",
    "nether": "Nether Terrain",
    "bastion": "Bastion",
    "fortress": "Fortress",
    "blind": "Blind",
    "stronghold": "Stronghold",
    "end": "The End",
}


def main(uuid, detailed_matches, elo, player_season, num_comps, rank_filter, playerbase_file):
    info_splits, death_splits = get_avg_splits(
        uuid, detailed_matches
    )
    ranked_splits = get_ranked_splits(info_splits["self"]["avg"], rank_filter, playerbase_file)
    polygon = get_polygon(ranked_splits)
    polygon = add_text(polygon, info_splits["self"]["avg"], ranked_splits, rank_filter)

    comments = {}
    comments["title"] = f"Split Performance"
    comments["description"] = (
        f"{len(detailed_matches)} games (with {num_comps} completions) were used in analysing your splits. {get_sample_size(num_comps)}"
    )
    comments["count"] = get_count(info_splits["self"]["completions"])
    if int(player_season) != 1:
        comments["player_deaths"], comments["opp_deaths"] = get_death_comments(
            death_splits, elo, rank_filter
        )
    comments["best"], comments["worst"] = get_best_worst(ranked_splits)

    return comments, polygon


def get_avg_splits(uuid, detailed_matches):
    info_splits = {
        "self": {
            "completions": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
                "time": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
                "avg": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
        },
        "opp": {
            "completions": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
                "time": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
                "avg": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
        }
    }
    death_splits = {
        "self": {
            "count": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
            "enters": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
            "rate": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
        },
        "opp": {
            "count": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
            "enters": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
            "rate": {
                "ow": 0,
                "nether": 0,
                "bastion": 0,
                "fortress": 0,
                "blind": 0,
                "stronghold": 0,
                "end": 0,
            },
        }
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

        prev_event = {"self": "ow", "opp": "ow"}
        prev_time = {"self": 0, "opp": 0}

        for event in reversed(match["timelines"]):
            player_type = "self" if event["uuid"] == uuid else "opp"

            if event["type"] == "projectelo.timeline.reset":
                prev_time[player_type] = event["time"]
                prev_event[player_type] = "ow"
                death_splits[player_type]["enters"][prev_event[player_type]] += 1
                death_opportunities[prev_event[player_type]] += 1

            elif event["type"] in event_mapping:
                split_length = event["time"] - prev_time[player_type]
                info_splits[player_type]["time"][prev_event[player_type]] += split_length
                info_splits[player_type]["completions"][prev_event[player_type]] += 1

                prev_time[player_type] = event["time"]
                prev_event[player_type] = event_mapping[event["type"]]
                death_splits[player_type]["enters"][prev_event[player_type]] += 1
                death_opportunities[prev_event[player_type]] += 1

            elif event["type"] == "projectelo.timeline.death":
                death_splits[player_type]["count"][prev_event[player_type]] += 1

        if match["forfeited"] is False:
            player_type = "self" if match["result"]["uuid"] == uuid else "opp"
            split_length = match["result"]["time"] - prev_time[player_type]
            info_splits[player_type]["time"][prev_event[player_type]] += split_length
            info_splits[player_type]["completions"][prev_event[player_type]] += 1

    for player_type in ("self", "opp"):
        for split in SPLIT_NAMING:
            if info_splits[player_type]["completions"][split] == 0:
                info_splits[player_type]["avg"][split] = 1000000000000
            else:
                info_splits[player_type]["avg"][split] = round(info_splits[player_type]["time"][split] / info_splits[player_type]["completions"][split])
            if death_splits[player_type]["enters"][split] == 0:
                death_splits[player_type]["rate"][split] = 0
            else:
                death_splits[player_type]["rate"][split] = round(death_splits[player_type]["count"][split] / death_splits[player_type]["enters"][split], 3)

    return info_splits, death_splits


def get_ranked_splits(average_splits, rank_filter, playerbase_file):
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
        val = ranked_splits[constants.SPLITS[i]]
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
            if ranked_splits[constants.SPLITS[i]] <= percentiles[j]:
                s_colour = percentile_colour[j]
                break
        if average_splits[constants.SPLITS[i]] == 1000000000000:
            stat = "No data"
        else:
            time = numb.digital_time(average_splits[constants.SPLITS[i]])
            stat = f"{time} / {word.percentify(ranked_splits[constants.SPLITS[i]])}"

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
            "This is a very low sample size. Lategame averages won't be reliable."
        )
    if num_comps < 20:
        return "This is an OK sample size."
    else:
        return "This is a large sample size and the data will reflect skill-level across each split properly."


def get_count(number_splits):
    names = " OW   / NETH / BAST / FORT / BLND / SH   / END  "
    count = ""
    for split in number_splits:
        num = number_splits[split]
        count += " " * (5 - len(str(num)))
        count += f"{num} "
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
        "value": f"{SPLIT_NAMING[max_key]} - `{word.percentify(ranked_splits[max_key])}`",
        "inline": True,
    }
    worst = {
        "name": f"Weakest Split",
        "value": f"{SPLIT_NAMING[min_key]} - `{word.percentify(ranked_splits[min_key])}`",
        "inline": True,
    }

    return [best, worst]


def get_death_comments(death_splits, elo, rank_filter):
    # Redundant atm
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
        differences[split_key] = death_splits["self"]["rate"][split_key] / overall_deaths[split_key]
        if differences[split_key] > max_diff:
            max_diff = differences[split_key]
            max_split = split_key


    values = []
    for player in ("self", "opp"):
        count = ""
        rate = ""
        for split in death_splits[player]["count"]:
            deaths = death_splits[player]["count"][split]
            death_rate = f"{numb.round_sf(death_splits[player]["rate"][split] * 100, 2)}%"
            count += " " * (5 - len(str(deaths)))
            count += f"{deaths} "
            rate += " " * (5 - len(str(death_rate)))
            rate += f"{death_rate} "
            if split != "end":
                count += "/"
                rate += "/"
        values.append(f"`|{count}|`\n`|{rate}|`")

    death_comment = {
        "name": "Death Rates",
        "value": values[0],
        "inline": False,
    }
    opp_comment = {
        "name": "Opponent Death Rates",
        "value": values[1],
        "inline": False,
    }
    return death_comment, opp_comment
