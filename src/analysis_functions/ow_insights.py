import math

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont

from rankedutils import constants, insight, numb, rank, word
from analysis_functions.bastion_insights import add_rank_img

SIDES = 5
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
OWS = list(constants.OW_MAPPING.values())
OW_NAMING = {
    "bt": "Buried Treasure",
    "dt": "Temple",
    "rp": "Ruined Portal",
    "ship": "Shipwreck",
    "village": "Village",
}
EMPTY_OWS = {ow: 0 for ow in OWS}
PERCENTILES = [0.3, 0.5, 0.7, 0.9, 0.95, 1.0]
PERCENTILE_COLOURS = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#3f82ff", "#ffd700"]


def main(uuid, detailed_matches, rank_filter, ows_final_boss):
    info_ows = get_avg_ows(uuid, detailed_matches)
    ranked_ows = get_ranked_ows(info_ows["self"]["avg"], rank_filter, ows_final_boss)
    polygon = get_polygon(ranked_ows)
    polygon = add_text(polygon, info_ows["self"]["avg"], ranked_ows, rank_filter)
    chart = get_chart(
        info_ows["timesaves"],
        info_ows["self"]["wins"],
        info_ows["opp"]["wins"],
        insight.get_avg_opponent_elo(uuid, detailed_matches)
    )

    comments = {}
    comments["title"] = f"Overworld Performance"
    comments["description"] = (
        f"{len(detailed_matches)} games were used in analysing this player's overworlds. {get_sample_size(len(detailed_matches))}"
    )
    comments["count"] = get_count(info_ows["self"]["completions"])
    comments["best"], comments["worst"] = get_best_worst(ranked_ows, info_ows["self"]["avg"])

    return comments, polygon, chart


def get_avg_ows(uuid, detailed_matches):
    info_ows = {
        "self": {
            "completions": EMPTY_OWS.copy(),
            "time": EMPTY_OWS.copy(),
            "avg": EMPTY_OWS.copy(),
            "wins": EMPTY_OWS.copy(),
        },
        "opp": {
            "completions": EMPTY_OWS.copy(),
            "time": EMPTY_OWS.copy(),
            "avg": EMPTY_OWS.copy(),
            "wins": EMPTY_OWS.copy(),
        },
        "timesaves": None
    }
    timesaves = {ow: [] for ow in OWS}

    for match in detailed_matches:
        if not match["timelines"]:
            continue

        ow_type = constants.OW_MAPPING[match["seedType"]]
        ow_entry = {"self": 0, "opp": 0}

        first_nether = {"self": None, "opp": None}

        for event in reversed(match["timelines"]):
            player_type = "self" if event["uuid"] == uuid else "opp"

            if event["type"] == "story.enter_the_nether":
                info_ows[player_type]["time"][ow_type] += event["time"] - ow_entry[player_type]
                info_ows[player_type]["completions"][ow_type] += 1

                if first_nether[player_type] is None:
                    first_nether[player_type] = event["time"]

            elif event["type"] == "projectelo.timeline.reset":
                ow_entry[player_type] = event["time"]

        if first_nether["self"] is not None and first_nether["opp"] is not None:
            timesave = first_nether["self"] - first_nether["opp"]
            winner = "self" if timesave < 0 else "opp"
            info_ows[winner]["wins"][ow_type] += 1
            timesaves[ow_type].append(timesave)

    info_ows["timesaves"] = {
        ow: round(np.median(timesaves[ow]))
        if timesaves[ow]
        else None
        for ow in timesaves
    }

    for player_type in ("self", "opp"):
        for ow_type in OWS:
            if info_ows[player_type]["completions"][ow_type] == 0:
                info_ows[player_type]["avg"][ow_type] = 1000000000000
            else:
                info_ows[player_type]["avg"][ow_type] = round(info_ows[player_type]["time"][ow_type] / info_ows[player_type]["completions"][ow_type])

    return info_ows


def get_ranked_ows(average_ows, rank_filter, ows_final_boss):
    ranked_ows = {"bt": 0, "dt": 0, "rp": 0, "ship": 0, "village": 0}

    lower, upper = rank.get_boundaries(rank_filter)

    for key in ows_final_boss:
        ows_sample = [
            attr[0]
            for attr in ows_final_boss[key]
            if rank_filter is None or (attr[1] and lower <= attr[1] < upper)
        ]
        ranked_ows[key] = np.searchsorted(
            ows_sample,
            average_ows[key],
        )
        if len(ows_sample) == 0:
            ranked_ows[key] = 0
        else:
            ranked_ows[key] = round(
                1 - ranked_ows[key] / len(ows_sample), 3
            )

    return ranked_ows


def get_polygon(ranked_ows):
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
    for i in range(len(ANGLES)):
        val = ranked_ows[OWS[i]]
        if val == 0:
            proportion = 100000
        else:
            proportion = INIT_PROP / val
        polygon_size = MIDDLE / proportion

        xy.append(
            (
                (math.cos(ANGLES[i]) + proportion) * polygon_size + OFFSET_X,
                (math.sin(ANGLES[i]) + proportion) * polygon_size + OFFSET_Y,
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


def add_text(polygon, average_ows, ranked_ows, rank_filter):
    text_prop = INIT_PROP * 0.95
    xy = []
    titles = list(OW_NAMING.values())

    big_size = 50
    big_font = ImageFont.truetype("minecraft_font.ttf", big_size)
    title_size = 30
    title_font = ImageFont.truetype("minecraft_font.ttf", title_size)
    stat_size = 25
    stat_font = ImageFont.truetype("minecraft_font.ttf", stat_size)

    big_title = "Overworld Performance"
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
            xy[i][0] += word.calc_length("Strongholdddl", title_size) / 2
            xy[i][1] -= (
                word.horiz_to_vert(title_size) / 2 + word.horiz_to_vert(stat_size) / 2
            )

        elif i == math.ceil(SIDES / 2) and SIDES % 2 == 1:
            xy[i][0] -= word.calc_length("Strongholdddl", title_size) / 8

        elif i == math.floor(SIDES / 2) and SIDES % 2 == 1:
            xy[i][0] += word.calc_length("Strongholdddl", title_size) / 8

        elif math.ceil(SIDES / 2) < i:
            xy[i][0] -= word.calc_length("Strongholdddl", title_size) / 2
            xy[i][1] -= (
                word.horiz_to_vert(title_size) / 2 + word.horiz_to_vert(stat_size) / 2
            )

    for i in range(SIDES):

        s_colour = PERCENTILE_COLOURS[0]
        for j in range(len(PERCENTILES)):
            if ranked_ows[OWS[i]] <= PERCENTILES[j]:
                s_colour = PERCENTILE_COLOURS[j]
                break
        if average_ows[OWS[i]] == 1000000000000:
            stat = "No data"
        else:
            time = numb.digital_time(average_ows[OWS[i]])
            stat = f"{time} / {word.percentify(ranked_ows[OWS[i]])}"

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
    col_width = (right - left) / len(OWS)
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
        for split in OWS
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
    for i in range(1, len(OWS)):
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
    sideways_draw.text((IMG_SIZE_Y - zero_y, IMG_SIZE_X - 30), "Split Winrate", font=label_font, anchor="mm", **outline)
    chart.alpha_composite(sideways.rotate(90, expand=True))

    # Timesave and axis labels
    for i, split in enumerate(OWS):
        x0, x1 = left + i * col_width, left + (i + 1) * col_width
        centre_x = (x0 + x1) / 2
        timesave = timesaves[split]

        x_axis_offset = 15
        if winrates[split] is not None:
            y = zero_y + (winrates[split] - 0.5) / wr_limit * half_height
            draw.line([(x0 + 15, y), (x1 - 15, y)], fill=winrate_colour, width=4)

        draw.text((centre_x, bottom + x_axis_offset), OW_NAMING[split], font=small_font, anchor="mt", **outline)

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

    draw.text((IMG_SIZE_X / 2, OFFSET_Y), "Overworld Timesaves", font=big_font, anchor="ma", **outline)
    draw.text((IMG_SIZE_X / 2, OFFSET_Y + 85), f"vs opponents averaging {avg_opp_elo} elo", muted, label_font, "mm", **outline)

    return chart


def get_sample_size(num_games):
    if num_games < 30:
        return "This is a very low sample size. Take these stats with a grain of salt."
    if num_games < 80:
        return "This is an OK sample size."
    else:
        return "This is a large sample size and the data will reflect overworld skill-levels properly."


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


def get_best_worst(ranked_ows, avg_ows):
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

    def ow_to_text(ow):
        if avg_ows[ow] == 1000000000000:
            return "`Not enough data`"
        else:
            time = numb.digital_time(avg_ows[ow])
            return f"`{time} ({word.percentify(ranked_ows[ow])})`"

    best = {
        "name": f"Strongest Seed Type - {OW_NAMING[max_key]}",
        "value": ow_to_text(max_key),
        "inline": True,
    }
    worst = {
        "name": f"Weakest Seed Type - {OW_NAMING[min_key]}",
        "value": ow_to_text(min_key),
        "inline": True,
    }

    return [best, worst]
