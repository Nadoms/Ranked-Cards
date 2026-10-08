import json
from os import path
import math

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont

from rankedutils import insight, word, numb, rank
from card_functions import add_badge

SIDES = 4
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
BASTION_TYPES = ["bridge", "housing", "stables", "treasure"]
BASTION_NAMING = {
    "bridge": "Bridge",
    "housing": "Housing",
    "stables": "Stables",
    "treasure": "Treasure",
}
EMPTY_BASTIONS = {bastion: 0 for bastion in BASTION_TYPES}
PERCENTILES = [0.3, 0.5, 0.7, 0.9, 0.95, 1.0]
PERCENTILE_COLOURS = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#3f82ff", "#ffd700"]


def main(uuid, detailed_matches, elo, player_season, rank_filter, bastions_final_boss):
    info_bastions, death_bastions = get_avg_bastions(
        uuid, detailed_matches
    )
    ranked_bastions = get_ranked_bastions(info_bastions["self"]["avg"], rank_filter, bastions_final_boss)
    polygon = get_polygon(ranked_bastions)
    polygon = add_text(polygon, info_bastions["self"]["avg"], ranked_bastions, rank_filter)
    chart = get_chart(
        info_bastions["timesaves"],
        info_bastions["self"]["wins"],
        info_bastions["opp"]["wins"],
        insight.get_avg_opponent_elo(uuid, detailed_matches)
    )
    sum_bastions = sum(info_bastions["self"]["completions"].values())

    comments = {}
    comments["title"] = f"Bastion Performance"
    comments["description"] = (
        f"{sum_bastions} completed bastion splits were used in analysing this player's performance. {get_sample_size(sum_bastions)}"
    )
    comments["count"] = get_count(info_bastions["self"]["completions"])
    if int(player_season) != 1:
        comments["player_deaths"], comments["opp_deaths"] = get_death_comments(
            death_bastions, elo, rank_filter
        )
    comments["best"], comments["worst"] = get_best_worst(ranked_bastions, info_bastions["self"]["avg"])

    return comments, polygon, chart


def get_avg_bastions(uuid, detailed_matches):
    info_bastions = {
        "self": {
            "completions": EMPTY_BASTIONS.copy(),
            "time": EMPTY_BASTIONS.copy(),
            "avg": EMPTY_BASTIONS.copy(),
            "wins": EMPTY_BASTIONS.copy(),
        },
        "opp": {
            "completions": EMPTY_BASTIONS.copy(),
            "time": EMPTY_BASTIONS.copy(),
            "avg": EMPTY_BASTIONS.copy(),
            "wins": EMPTY_BASTIONS.copy(),
        },
        "timesaves": None
    }
    death_bastions = {
        "self": {
            "count": EMPTY_BASTIONS.copy(),
            "enters": EMPTY_BASTIONS.copy(),
            "rate": EMPTY_BASTIONS.copy(),
        },
        "opp": {
            "count": EMPTY_BASTIONS.copy(),
            "enters": EMPTY_BASTIONS.copy(),
            "rate": EMPTY_BASTIONS.copy(),
        },
    }
    death_opportunities = {"bridge": 0, "housing": 0, "stables": 0, "treasure": 0}
    timesaves = {bastion: [] for bastion in BASTION_TYPES}
    bastion_conditions = [
        "nether.obtain_crying_obsidian",
        "nether.loot_bastion",
        "story.form_obsidian",
    ]
    post_bastion = [
        "nether.find_fortress",
        "projectelo.timeline.blind_travel",
        "story.follow_ender_eye",
        "story.enter_the_end",
    ]

    for match in detailed_matches:
        if not match["timelines"] or not match["bastionType"]:
            continue

        bastion_type = match["bastionType"].lower()
        bastion_entry = {"self": 0, "opp": 0}
        bastion_exit = {"self": 0, "opp": 0}
        bastion_progression = {"self": 0, "opp": 0}

        bastion_entry_persistent = {"self": None, "opp": None}
        bastion_length_persistent = {"self": None, "opp": None}

        for event in reversed(match["timelines"]):
            player_type = "self" if event["uuid"] == uuid else "opp"

            # If entering bastion, set entry time.
            if event["type"] == "nether.find_bastion":
                bastion_entry[player_type] = event["time"]
                if bastion_entry_persistent[player_type] is None:
                    bastion_entry_persistent[player_type] = event["time"]
                death_bastions[player_type]["enters"][bastion_type] += 1

            # If resetting, set everything to how it was.
            elif event["type"] == "projectelo.timeline.reset":
                bastion_entry[player_type] = 0
                bastion_progression[player_type] = 0

            # If currently inside the bastion,
            elif bastion_entry[player_type] and not bastion_exit[player_type]:
                # If doing bastion things, increase the bastion progression.
                if event["type"] in bastion_conditions:
                    bastion_progression[player_type] += 1

                # If dying during the bastion, increment the death count.
                elif event["type"] == "projectelo.timeline.death":
                    death_bastions[player_type]["count"][bastion_type] += 1

                # If entering another split after bastion, set the exit time.
                elif event["type"] in post_bastion:
                    bastion_exit[player_type] = event["time"]
                    bastion_length = bastion_exit[player_type] - bastion_entry[player_type]
                    info_bastions[player_type]["time"][bastion_type] += bastion_length
                    info_bastions[player_type]["completions"][bastion_type] += 1

                    if bastion_length_persistent[player_type] is None:
                        bastion_length_persistent[player_type] = event["time"] - bastion_entry_persistent[player_type]

        self_length = bastion_length_persistent["self"]
        opp_length = bastion_length_persistent["opp"]
        if self_length is not None and opp_length is not None:
            timesave = self_length - opp_length
            winner = "self" if timesave < 0 else "opp"
            info_bastions[winner]["wins"][bastion_type] += 1
            timesaves[bastion_type].append(timesave)

    info_bastions["timesaves"] = {
        bastion: round(np.median(timesaves[bastion]))
        if timesaves[bastion]
        else None
        for bastion in timesaves
    }

    for player_type in ("self", "opp"):
        for bastion in BASTION_TYPES:
            if info_bastions[player_type]["completions"][bastion] == 0:
                info_bastions[player_type]["avg"][bastion] = 1000000000000
            else:
                info_bastions[player_type]["avg"][bastion] = round(info_bastions[player_type]["time"][bastion] / info_bastions[player_type]["completions"][bastion])
            if death_bastions[player_type]["enters"][bastion] == 0:
                death_bastions[player_type]["rate"][bastion] = 0
            else:
                death_bastions[player_type]["rate"][bastion] = round(death_bastions[player_type]["count"][bastion] / death_bastions[player_type]["enters"][bastion], 3)

    return info_bastions, death_bastions


def get_ranked_bastions(average_bastions, rank_filter, bastions_final_boss):
    ranked_bastions = {"bridge": 0, "housing": 0, "stables": 0, "treasure": 0}

    lower, upper = rank.get_boundaries(rank_filter)

    for key in bastions_final_boss:
        bastions_sample = [
            attr[0]
            for attr in bastions_final_boss[key]
            if rank_filter is None or (attr[1] and lower <= attr[1] < upper)
        ]
        ranked_bastions[key] = np.searchsorted(
            bastions_sample,
            average_bastions[key],
        )
        if len(bastions_sample) == 0:
            ranked_bastions[key] = 0
        else:
            ranked_bastions[key] = round(
                1 - ranked_bastions[key] / len(bastions_sample), 3
            )

    return ranked_bastions


def get_polygon(ranked_bastions):
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
        val = ranked_bastions[BASTION_TYPES[i]]
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

    stops = {0: PERCENTILE_COLOURS[1], 0.25: PERCENTILE_COLOURS[2], 1: PERCENTILE_COLOURS[4]}
    rgb = np.array([ImageColor.getrgb(colour) for colour in stops.values()])
    gradient = np.dstack([np.interp(distance, list(stops), rgb[:, channel]) for channel in range(3)])

    # Fill with gradient
    mask = Image.new("L", (IMG_SIZE_X, IMG_SIZE_Y))
    ImageDraw.Draw(mask).polygon(xy, fill=255)
    polygon_frame.paste(Image.fromarray(gradient.astype(np.uint8)), mask=mask)
    stats_draw.polygon(xy, outline="#c0e4ff", width=4)

    polygon = Image.blend(polygon_frame, polygon_stats, 0.4)

    return polygon


def add_text(polygon, average_bastions, ranked_bastions, rank_filter):
    text_prop = INIT_PROP * 0.95
    xy = []
    titles = list(BASTION_NAMING.values())

    big_size = 50
    big_font = ImageFont.truetype("minecraft_font.ttf", big_size)
    title_size = 30
    title_font = ImageFont.truetype("minecraft_font.ttf", title_size)
    stat_size = 25
    stat_font = ImageFont.truetype("minecraft_font.ttf", stat_size)

    big_title = "Bastion Performance"
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
            xy[i][0] += word.calc_length("Treasureeee", title_size) / 2
            xy[i][1] -= (
                word.horiz_to_vert(title_size) / 2 + word.horiz_to_vert(stat_size) / 2
            )

        elif i == math.ceil(SIDES / 2) and SIDES % 2 == 1:
            xy[i][0] -= word.calc_length("Treasureeee", title_size) / 8

        elif i == math.floor(SIDES / 2) and SIDES % 2 == 1:
            xy[i][0] += word.calc_length("Treasureeee", title_size) / 8

        elif math.ceil(SIDES / 2) < i:
            xy[i][0] -= word.calc_length("Treasureeee", title_size) / 2
            xy[i][1] -= (
                word.horiz_to_vert(title_size) / 2 + word.horiz_to_vert(stat_size) / 2
            )

    for i in range(SIDES):

        s_colour = PERCENTILE_COLOURS[0]
        for j in range(len(PERCENTILES)):
            if ranked_bastions[BASTION_TYPES[i]] <= PERCENTILES[j]:
                s_colour = PERCENTILE_COLOURS[j]
                break
        if average_bastions[BASTION_TYPES[i]] == 1000000000000:
            stat = "No data"
        else:
            time = numb.digital_time(average_bastions[BASTION_TYPES[i]])
            stat = f"{time} / {word.percentify(ranked_bastions[BASTION_TYPES[i]])}"

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


def add_rank_img(polygon, rank_filter, coords, title_size):
    badge = add_badge.get_badge(rank_filter, 7)
    dim = badge.size[0]
    badge_x1 = coords[0] - dim - 20
    badge_x2 = IMG_SIZE_X - coords[0] + 20
    badge_y = int(coords[1] + word.horiz_to_vert(title_size) / 2 - dim / 2)

    polygon.paste(badge, (badge_x1, badge_y), badge)
    polygon.paste(badge, (badge_x2, badge_y), badge)
    return polygon


def get_chart(timesaves, self_wins, opp_wins, avg_opp_elo):
    left, right = 120, IMG_SIZE_X - 110
    top, bottom = 160, 700
    zero_y = (top + bottom) / 2
    half_height = (bottom - top) / 2
    col_width = (right - left) / len(BASTION_TYPES)
    muted = "#b3c4c9"
    self_colour = "#3f82ff"
    opp_colour = "#f12d2d"
    bar_stroke = "#c0e4ff"
    winrate_colour = "#ffff40A0"
    bg_colour = "#413348"
    bg__stroke = "#515368"
    outline = {"stroke_fill": "#000000", "stroke_width": 2}

    label_font = ImageFont.truetype("minecraft_font.ttf", 20)
    small_font = ImageFont.truetype("minecraft_font.ttf", 18)
    big_font = ImageFont.truetype("minecraft_font.ttf", 50)

    winrates = {
        split: self_wins[split] / (self_wins[split] + opp_wins[split]) if self_wins[split] + opp_wins[split] else None
        for split in BASTION_TYPES
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
    for i in range(1, len(BASTION_TYPES)):
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
    for i, split in enumerate(BASTION_TYPES):
        x0, x1 = left + i * col_width, left + (i + 1) * col_width
        centre_x = (x0 + x1) / 2
        timesave = timesaves[split]

        x_axis_offset = 15
        if winrates[split] is not None:
            y = zero_y + (winrates[split] - 0.5) / wr_limit * half_height
            draw.line([(x0 + 15, y), (x1 - 15, y)], fill=winrate_colour, width=4)

        draw.text((centre_x, bottom + x_axis_offset), BASTION_NAMING[split], font=small_font, anchor="mt", **outline)

        if timesave is None:
            draw.text((centre_x, zero_y - 2), "No data", muted, label_font, "mm", **outline)
        else:
            y = zero_y - timesave / timesave_limit * half_height
            colour = tuple(min(col + 128, 255) for col in gradient.getpixel((centre_x, y - top)))
            draw.text(
                (centre_x, y - 2),
                format_time(timesave),
                colour,
                label_font,
                "mm",
                **outline
            )

    draw.text((IMG_SIZE_X / 2, OFFSET_Y), "Bastion Timesaves", font=big_font, anchor="ma", **outline)
    draw.text((IMG_SIZE_X / 2, OFFSET_Y + 85), f"vs opponents averaging {avg_opp_elo} elo", muted, label_font, "mm", **outline)

    return chart


def get_sample_size(sum_bastions):
    if sum_bastions < 24:
        return "This is a very low sample size. Take these stats with a grain of salt."
    if sum_bastions < 60:
        return "This is an OK sample size."
    else:
        return "This is a large sample size and the data will reflect bastion skill-levels properly."


def get_count(completed_bastions):
    names = " BRDG / HOUS / STBL / TRSR "
    count = ""
    for bastion in completed_bastions:
        num = completed_bastions[bastion]
        count += " " * (5 - len(str(num)))
        count += f"{num} "
        if bastion != "treasure":
            count += "/"
    value = f"`|{names}|`\n`|{count}|`"

    count_comment = {
        "name": "Bastion Counts",
        "value": value,
        "inline": False,
    }
    return count_comment


def get_best_worst(ranked_bastions, avg_bastions):
    max_key = ""
    max_val = -1
    min_key = ""
    min_val = 1000000000000000000

    for key in ranked_bastions:
        if ranked_bastions[key] > max_val:
            max_val = ranked_bastions[key]
            max_key = key

        if ranked_bastions[key] < min_val:
            min_val = ranked_bastions[key]
            min_key = key

    def bastion_to_text(bastion):
        if avg_bastions[bastion] == 1000000000000:
            return "`Not enough data`"
        else:
            time = numb.digital_time(avg_bastions[bastion])
            return f"`{time} ({word.percentify(ranked_bastions[bastion])})`"

    best = {
        "name": f"Strongest Bastion - {max_key.capitalize()}",
        "value": bastion_to_text(max_key),
        "inline": True,
    }
    worst = {
        "name": f"Weakest Bastion - {min_key.capitalize()}",
        "value": bastion_to_text(min_key),
        "inline": True,
    }

    return [best, worst]


def get_death_comments(death_bastions, elo, rank_filter):
    # Redundant atm
    differences = {"bridge": 0, "housing": 0, "stables": 0, "treasure": 0}

    if rank_filter is None:
        player_rank = rank.get_rank(elo)
        if player_rank == rank.Rank.UNRANKED:
            player_rank = rank.Rank.GOLD
    else:
        player_rank = rank_filter
    file = path.join("src", "database", "deaths.json")
    with open(file, "r", encoding="UTF-8") as f:
        overall_deaths = json.load(f)["bastions"][str(player_rank.value)]

    max_diff = 0
    max_bastion = None
    for bastion_key in differences:
        differences[bastion_key] = (
            death_bastions["self"]["rate"][bastion_key] / overall_deaths[bastion_key]
        )
        if differences[bastion_key] > max_diff:
            max_diff = differences[bastion_key]
            max_bastion = bastion_key


    values = []
    for player in ("self", "opp"):
        count = ""
        rate = ""
        for bastion in death_bastions[player]["count"]:
            deaths = death_bastions[player]["count"][bastion]
            death_rate = f"{numb.round_sf(death_bastions[player]["rate"][bastion] * 100, 2)}%"
            count += " " * (5 - len(str(deaths)))
            count += f"{deaths} "
            rate += " " * (5 - len(str(death_rate)))
            rate += f"{death_rate} "
            if bastion != "treasure":
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
