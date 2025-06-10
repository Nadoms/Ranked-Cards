from PIL import ImageDraw, ImageFont

from gen_functions import db, word, rank


def write(chart, uuids, response, vs_response):
    statted_image = ImageDraw.Draw(chart)
    stat_size = 20
    stat_font = ImageFont.truetype("minecraft_font.ttf", stat_size)
    middle = 600
    x_values = [middle + 370, middle - 370]
    y_values = [180, 210, 240]

    for i in range(0, 2):
        stats = get_stats(response, uuids, i)
        legacy_elo_colour = rank.get_colour(stats[0][1])[:2]
        current_elo_colour = rank.get_colour(stats[1][1])[:2]
        score_colour = ["#00ffff", "#122b30"]
        colours = [legacy_elo_colour, current_elo_colour]

        for j, stat_words in enumerate(stats):
            overall_line = ""
            for k in range(len(stats[j])):
                if stats[j][k] is None:
                    stats[j][k] = "unranked"
                else:
                    stats[j][k] = str(stats[j][k])
                overall_line += stats[j][k]

            x = int(x_values[i] - i * word.calc_length(overall_line, stat_size))

            for k, stat_word in enumerate(stat_words):
                y = y_values[j] - int(word.horiz_to_vert(stat_size) / 2) + i * 180

                if k == 1 and j <= 1:
                    f_colour, s_colour = colours[j]
                else:
                    f_colour, s_colour = score_colour
                statted_image.text(
                    (x, y),
                    stat_word,
                    font=stat_font,
                    fill=f_colour,
                    stroke_fill=s_colour,
                    stroke_width=1,
                )

                x += int(word.calc_length(stat_word, stat_size))

    return chart


def get_stats(response, uuids, i):
    if "eloRate" not in response["players"][i]:
        _, cursor = db.start()
        current_elo = db.get_elo(cursor, uuids[i])
    else:
        current_elo = response["players"][i]["eloRate"]
    legacy_elo = None
    change_elo = None
    for score_change in response["changes"]:
        if score_change["uuid"] == uuids[i]:
            legacy_elo = score_change["eloRate"]
            change_elo = score_change["change"]
    change_msg = (
        f"{'lost' if change_elo < 0 else 'won'}"
        f" {abs(change_elo)} "
        " elo"
    ) if change_elo is not None else "no elo change"

    return [
        ["was ", legacy_elo, " elo" if legacy_elo is not None else ""],
        ["now ", current_elo, " elo" if current_elo is not None else ""],
        [change_msg],
    ]
