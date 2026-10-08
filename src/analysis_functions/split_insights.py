import json
from os import path
import math

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont

from rankedutils import constants, word, numb, rank, insight
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
    "nether": "Nether",
    "bastion": "Bastion",
    "fortress": "Fortress",
    "blind": "Blind",
    "stronghold": "Stronghold",
    "end": "The End",
}
EMPTY_SPLITS = {split: 0 for split in SPLIT_NAMING}
EMPTY_SPLITS_ENDLESS = {split: 0 for split in SPLIT_NAMING if split != "end"}
NULL_SPLITS_ENDLESS = {split: None for split in SPLIT_NAMING if split != "end"}
PERCENTILES = [0.3, 0.5, 0.7, 0.9, 0.95, 1.0]
PERCENTILE_COLOURS = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#3f82ff", "#ffd700"]


def main(uuid, detailed_matches, elo, player_season, num_comps, rank_filter, splits_final_boss):
    info_splits, death_splits = get_avg_splits(
        uuid, detailed_matches
    )
    ranked_splits = get_ranked_splits(info_splits["self"]["avg"], rank_filter, splits_final_boss)
    polygon = get_polygon(ranked_splits)
    polygon = add_text(polygon, info_splits["self"]["avg"], ranked_splits, rank_filter)
    chart = get_chart(
        info_splits["timesaves"],
        info_splits["self"]["wins"],
        info_splits["opp"]["wins"],
        insight.get_avg_opponent_elo(uuid, detailed_matches)
    )

    comments = {}
    comments["title"] = f"Split Performance"
    comments["description"] = (
        f"{len(detailed_matches)} games (with {num_comps} completions) were used in analysing this player's splits. {get_sample_size(num_comps)}"
    )
    comments["count"] = get_count(info_splits["self"]["completions"])
    if int(player_season) != 1:
        comments["player_deaths"], comments["opp_deaths"] = get_death_comments(
            death_splits, elo, rank_filter
        )
    comments["best"], comments["worst"] = get_best_worst(ranked_splits, info_splits["self"]["avg"])

    return comments, polygon, chart


def get_avg_splits(uuid, detailed_matches):
    info_splits = {
        "self": {
            "completions": EMPTY_SPLITS.copy(),
            "time": EMPTY_SPLITS.copy(),
            "avg": EMPTY_SPLITS.copy(),
            "wins": EMPTY_SPLITS_ENDLESS.copy(),
        },
        "opp": {
            "completions": EMPTY_SPLITS.copy(),
            "time": EMPTY_SPLITS.copy(),
            "avg": EMPTY_SPLITS.copy(),
            "wins": EMPTY_SPLITS_ENDLESS.copy(),
        },
        "timesaves": None
    }
    death_splits = {
        "self": {
            "count": EMPTY_SPLITS.copy(),
            "enters": EMPTY_SPLITS.copy(),
            "rate": EMPTY_SPLITS.copy(),
        },
        "opp": {
            "count": EMPTY_SPLITS.copy(),
            "enters": EMPTY_SPLITS.copy(),
            "rate": EMPTY_SPLITS.copy(),
        }
    }
    death_opportunities = EMPTY_SPLITS.copy()
    timesaves = {split: [] for split in NULL_SPLITS_ENDLESS}
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
        death_splits["self"]["enters"]["ow"] += 1
        death_splits["opp"]["enters"]["ow"] += 1

        prev_event_persistent = {"self": "ow", "opp": "ow"}
        prev_time_persistent = {"self": 0, "opp": 0}
        split_times_persistent = {"self": NULL_SPLITS_ENDLESS.copy(), "opp": NULL_SPLITS_ENDLESS.copy()}

        for event in reversed(match["timelines"]):
            player_type = "self" if event["uuid"] == uuid else "opp"

            if event["type"] == "projectelo.timeline.reset":
                prev_time[player_type] = event["time"]
                prev_event[player_type] = "ow"
                death_splits[player_type]["enters"][prev_event[player_type]] += 1
                death_opportunities[prev_event[player_type]] += 1

            elif event["type"] in event_mapping:
                split_length = event["time"] - prev_time[player_type]
                split_length_persistent = event["time"] - prev_time_persistent[player_type]

                info_splits[player_type]["time"][prev_event[player_type]] += split_length
                info_splits[player_type]["completions"][prev_event[player_type]] += 1
                split_times_persistent[player_type][prev_event_persistent[player_type]] = split_length_persistent

                prev_time_persistent[player_type] = prev_time[player_type] = event["time"]
                prev_event_persistent[player_type] = prev_event[player_type] = event_mapping[event["type"]]
                death_splits[player_type]["enters"][prev_event[player_type]] += 1
                death_opportunities[prev_event[player_type]] += 1

            elif event["type"] == "projectelo.timeline.death":
                death_splits[player_type]["count"][prev_event[player_type]] += 1

        if match["forfeited"] is False:
            player_type = "self" if match["result"]["uuid"] == uuid else "opp"
            split_length = match["result"]["time"] - prev_time[player_type]
            info_splits[player_type]["time"][prev_event[player_type]] += split_length
            info_splits[player_type]["completions"][prev_event[player_type]] += 1

        for split in NULL_SPLITS_ENDLESS:
            self_time = split_times_persistent["self"][split]
            opp_time = split_times_persistent["opp"][split]
            if self_time is None or opp_time is None:
                continue
            timesave = self_time - opp_time
            winner = "self" if timesave < 0 else "opp"
            info_splits[winner]["wins"][split] += 1
            timesaves[split].append(timesave)

    info_splits["timesaves"] = {
        split: round(np.median(timesaves[split]))
        if timesaves[split]
        else None
        for split in timesaves
    }

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


def get_ranked_splits(average_splits, rank_filter, splits_final_boss):
    ranked_splits = EMPTY_SPLITS.copy()

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

    # Polygonal gradient
    xs, ys = np.meshgrid(np.arange(IMG_SIZE_X) - (MIDDLE + OFFSET_X), np.arange(IMG_SIZE_Y) - (MIDDLE + OFFSET_Y))
    edge_angles = [angle + math.pi / SIDES for angle in ANGLES]
    edge_distance = MIDDLE / INIT_PROP * math.cos(math.pi / SIDES)
    distance = np.max([xs * math.cos(angle) + ys * math.sin(angle) for angle in edge_angles], axis=0) / edge_distance

    stops = {0: PERCENTILE_COLOURS[1], 0.5: PERCENTILE_COLOURS[2], 1: PERCENTILE_COLOURS[4]}
    rgb = np.array([ImageColor.getrgb(colour) for colour in stops.values()])
    gradient = np.dstack([np.interp(distance, list(stops), rgb[:, channel]) for channel in range(3)])

    # Fill with gradient
    mask = Image.new("L", (IMG_SIZE_X, IMG_SIZE_Y))
    ImageDraw.Draw(mask).polygon(xy, fill=255)
    polygon_frame.paste(Image.fromarray(gradient.astype(np.uint8)), mask=mask)
    stats_draw.polygon(xy, outline="#a1d3f8", width=4)

    polygon = Image.blend(polygon_frame, polygon_stats, 0.4)

    return polygon


def add_text(polygon, average_splits, ranked_splits, rank_filter):
    text_prop = INIT_PROP * 0.95
    xy = []
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
        s_colour = PERCENTILE_COLOURS[0]
        for j in range(len(PERCENTILES)):
            if ranked_splits[constants.SPLITS[i]] <= PERCENTILES[j]:
                s_colour = PERCENTILE_COLOURS[j]
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


def get_chart(timesaves, self_wins, opp_wins, avg_opp_elo):
    left, right = 120, IMG_SIZE_X - 110
    top, bottom = 160, 700
    zero_y = (top + bottom) / 2
    half_height = (bottom - top) / 2
    col_width = (right - left) / len(EMPTY_SPLITS_ENDLESS)
    muted = "#b3c4c9"
    self_colour = "#3f82ff"
    opp_colour = "#f12d2d"
    bar_stroke = "#a1d3f8"
    winrate_colour = "#ffff40A0"
    bg_colour = "#413348"
    bg__stroke = "#515368"
    outline = {"stroke_fill": "#000000", "stroke_width": 2}

    label_font = ImageFont.truetype("minecraft_font.ttf", 20)
    small_font = ImageFont.truetype("minecraft_font.ttf", 18)
    big_font = ImageFont.truetype("minecraft_font.ttf", 50)

    winrates = {
        split: self_wins[split] / (self_wins[split] + opp_wins[split]) if self_wins[split] + opp_wins[split] else None
        for split in EMPTY_SPLITS_ENDLESS
    }

    max_timesave = max((abs(timesave) for timesave in timesaves.values() if timesave is not None), default=0)
    step = 2000 if max_timesave <= 10000 else 10000
    timesave_limit = math.ceil(max_timesave / step) * step if max_timesave else 2000
    max_dev = max((abs(wr - 0.5) for wr in winrates.values() if wr is not None), default=0)
    wr_limit = math.ceil(max_dev * 10) / 10 if max_dev else 0.1

    def format_time(time):
        sign = "+" if time > 0 else "-" if time < 0 else ""
        time = abs(time)
        if time >= 10000 or time % 1000 == 0:
            return f"{sign}{round(time / 1000)}s"
        return f"{sign}{time / 1000:.1f}s"

    # Gradients
    plot_size = (IMG_SIZE_X, bottom - top + 1)
    gradient = Image.composite(
        Image.new("RGBA", plot_size, self_colour),
        Image.new("RGBA", plot_size, opp_colour),
        Image.linear_gradient("L").resize(plot_size),
    )

    chart_frame = Image.new("RGBA", (IMG_SIZE_X, IMG_SIZE_Y))
    frame_draw = ImageDraw.Draw(chart_frame)

    # Footprint
    frame_draw.rectangle((left, top, right, bottom), fill=bg_colour)
    for i in (-2, -1, 1, 2):
        y = zero_y - i / 2 * half_height
        frame_draw.line([(left, y), (right, y)], fill=bg__stroke, width=3)
    for i in range(1, len(EMPTY_SPLITS_ENDLESS)):
        x = left + i * col_width
        frame_draw.line([(x, top), (x, bottom)], fill=bg__stroke, width=3)

    chart_stats = chart_frame.copy()

    # Timesave bars
    for i, timesave in enumerate(timesaves.values()):
        if not timesave:
            continue
        x0 = left + i * col_width
        x1 = x0 + col_width
        y = zero_y - timesave / timesave_limit * half_height
        y0 = min(zero_y, y)
        y1 = max(zero_y, y)
        box = tuple(round(v) for v in (x0, y0, x1, y1))
        chart_frame.paste(gradient.crop((box[0], box[1] - top, box[2], box[3] - top)), box)
        frame_draw.rectangle(box, outline=bar_stroke, width=2)

    chart = Image.blend(chart_frame, chart_stats, 0.4)
    draw = ImageDraw.Draw(chart)

    # Axes
    draw.line([(left, top), (left, bottom)], width=4)
    draw.line([(right, top), (right, bottom)], width=4)
    draw.line([(left, zero_y), (right, zero_y)], width=4)

    y_axis_offset = 10
    for i in (-2, -1, 0, 1, 2):
        y = zero_y - i / 2 * half_height
        draw.text((left - y_axis_offset, y), format_time(timesave_limit * i / 2), muted, small_font, "rm", **outline)
        draw.text((right + y_axis_offset, y), f"{round((0.5 - wr_limit * i / 2) * 100)}%", muted, small_font, "lm", **outline)

    # Axes titles
    sideways = Image.new("RGBA", (IMG_SIZE_Y, IMG_SIZE_X))
    sideways_draw = ImageDraw.Draw(sideways)
    sideways_draw.text((IMG_SIZE_Y - zero_y, 35), "Median Timesave", font=label_font, anchor="mm", **outline)
    sideways_draw.text((IMG_SIZE_Y - zero_y, IMG_SIZE_X - 30), "Winrate", font=label_font, anchor="mm", **outline)
    chart.alpha_composite(sideways.rotate(90, expand=True))

    # Timesave and axis labels
    for i, split in enumerate(EMPTY_SPLITS_ENDLESS):
        x0, x1 = left + i * col_width, left + (i + 1) * col_width
        centre_x = (x0 + x1) / 2
        timesave = timesaves[split]

        x_axis_offset = 15
        if winrates[split] is not None:
            y = zero_y + (winrates[split] - 0.5) / wr_limit * half_height
            draw.line([(x0 + 15, y), (x1 - 15, y)], fill=winrate_colour, width=4)

        draw.text((centre_x, bottom + x_axis_offset), SPLIT_NAMING[split], font=small_font, anchor="mt", **outline)

        if timesave is None:
            draw.text((centre_x, zero_y - 2), "No data", muted, small_font, "mm", **outline)
        else:
            y = zero_y - timesave / timesave_limit * half_height
            colour = tuple(min(col + 100, 255) for col in gradient.getpixel((centre_x, y - top)))
            draw.text(
                (centre_x, y - 2),
                format_time(timesave),
                colour,
                label_font,
                "mm",
                **outline
            )

    draw.text((IMG_SIZE_X / 2, OFFSET_Y), "Split Timesaves", font=big_font, anchor="ma", **outline)
    draw.text((IMG_SIZE_X / 2, OFFSET_Y + 85), f"vs opponents averaging {avg_opp_elo} elo", muted, label_font, "mm", **outline)

    return chart


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


def get_best_worst(ranked_splits, avg_splits):
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

    def split_to_text(split):
        if avg_splits[split] == 1000000000000:
            return "`Not enough data`"
        else:
            time = numb.digital_time(avg_splits[split])
            return f"`{time} ({word.percentify(ranked_splits[split])})`"

    best = {
        "name": f"Strongest Split - {SPLIT_NAMING[max_key]}",
        "value": split_to_text(max_key),
        "inline": True,
    }
    worst = {
        "name": f"Weakest Split - {SPLIT_NAMING[min_key]}",
        "value": split_to_text(min_key),
        "inline": True,
    }

    return [best, worst]


def get_death_comments(death_splits, elo, rank_filter):
    # Redundant atm
    differences = EMPTY_SPLITS.copy()

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
