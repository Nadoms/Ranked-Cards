import math

from PIL import ImageDraw, ImageFont

from gen_functions import games, word, rank, numb


def write(card, response):
    statted_image = ImageDraw.Draw(card)
    stat_font = ImageFont.truetype("minecraft_font.ttf", 40)
    large_stat_font = ImageFont.truetype("minecraft_font.ttf", 60)

    colour = rank.get_colour(response["eloRate"])
    best_colour = rank.get_colour(response["seasonResult"]["highest"])
    rank_colour = [
        "#888888",
        "#b3c4c9",
        "#86b8db",
        "#50fe50",
        "#0f52ba",
        "#cd7f32",
        "#c0c0c0",
        "#ffd700",
    ]
    ws_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#0f52fa", "#ffd700"]
    ff_loss_colour = ["#bb3030", "#ff6164", "#86b8db", "#50fe50", "#0f52fa", "#ffd700"]
    elos = [0, 600, 900, 1200, 1500, 2000]
    w_d_l_colour = ["#86b8db", "#ee4b2b", "#ffbf00"]
    white = "#ffffff"

    # Season stats
    season_stats = get_season_stats(response)

    statted_image.text((1350, 50), "Season Stats", font=large_stat_font, fill=white)
    for i in range(0, len(season_stats[0])):
        statted_image.text(
            (1350, 140 + i * 60), season_stats[0][i], font=stat_font, fill=white
        )

    for i in range(0, len(season_stats[1])):
        if i == 0:
            w_d_l_spliced = season_stats[1][i].split("/")
            letters_placed = ""
            for j in range(0, len(w_d_l_spliced)):
                statted_image.text(
                    (
                        1827
                        - word.calc_length(season_stats[1][i], 40)
                        + word.calc_length(letters_placed, 40),
                        140 + i * 60,
                    ),
                    w_d_l_spliced[j],
                    font=stat_font,
                    fill=w_d_l_colour[j],
                )
                letters_placed += w_d_l_spliced[j]
                if j != len(w_d_l_spliced) - 1:
                    statted_image.text(
                        (
                            1827
                            - word.calc_length(season_stats[1][i], 40)
                            + word.calc_length(letters_placed, 40),
                            140 + i * 60,
                        ),
                        "/",
                        font=stat_font,
                        fill=white,
                    )
                    letters_placed += "/"
        elif i == 1:
            if season_stats[1][i] == "None":
                season_stats[1][i] = "-"
            statted_image.text(
                (1827 - word.calc_length(season_stats[1][i], 40), 140 + i * 60),
                season_stats[1][i],
                font=stat_font,
                fill=best_colour[0],
                stroke_fill=best_colour[1],
                stroke_width=1,
            )
        elif i == 2:
            if season_stats[1][i] != "-":
                rounded_ff_loss = float(season_stats[1][i])
                if rounded_ff_loss > 80:
                    rounded_ff_loss = 0
                elif rounded_ff_loss > 60:
                    rounded_ff_loss = 1
                elif rounded_ff_loss > 40:
                    rounded_ff_loss = 2
                elif rounded_ff_loss > 30:
                    rounded_ff_loss = 3
                elif rounded_ff_loss > 20:
                    rounded_ff_loss = 4
                elif rounded_ff_loss >= 0:
                    rounded_ff_loss = 5
                else:
                    rounded_ff_loss = 0
                season_stats[1][i] += "%"
            else:
                rounded_ff_loss = 0
            statted_image.text(
                (1827 - word.calc_length(season_stats[1][i], 40), 140 + i * 60),
                season_stats[1][i],
                font=stat_font,
                fill=ff_loss_colour[rounded_ff_loss],
            )
        elif i == 3:
            if season_stats[1][i] == ":00":
                season_stats[1][i] = "-"
                rounded_avg_completion = 0
            else:
                real_avg_completion = games.get_avg_completion(response, "season")
                rounded_avg_completion = rank.get_rank(
                    rank.get_elo_equivalent(real_avg_completion, "avg")
                )

            avg_colours = rank.get_colour(elos[rounded_avg_completion])
            statted_image.text(
                (1827 - word.calc_length(season_stats[1][i], 40), 140 + i * 60),
                season_stats[1][i],
                font=stat_font,
                fill=avg_colours[0],
                stroke_fill=avg_colours[1],
                stroke_width=1,
            )
        else:
            statted_image.text(
                (1827 - word.calc_length(season_stats[1][i], 40), 140 + i * 60),
                season_stats[1][i],
                font=stat_font,
                fill=white,
            )

    # Lifetime stats
    lifetime_stats = get_lifetime_stats(response)

    statted_image.text((1350, 480), "Lifetime Stats", font=large_stat_font, fill=white)
    for i in range(0, len(lifetime_stats[0])):
        statted_image.text(
            (1350, 570 + i * 60), lifetime_stats[0][i], font=stat_font, fill=white
        )

    for i in range(0, len(lifetime_stats[1])):
        if i == 3:
            rounded_best_ws = min(
                math.floor(int(lifetime_stats[1][i]) / 2), len(ws_colour) - 1
            )
            lifetime_stats[1][i] += " wins"
            statted_image.text(
                (1827 - word.calc_length(lifetime_stats[1][i], 40), 570 + i * 60),
                lifetime_stats[1][i],
                font=stat_font,
                fill=ws_colour[rounded_best_ws],
            )
        else:
            statted_image.text(
                (1827 - word.calc_length(lifetime_stats[1][i], 40), 570 + i * 60),
                lifetime_stats[1][i],
                font=stat_font,
                fill=white,
            )

    # Major stats
    major_stats = get_major_stats(response)

    for i in range(0, len(major_stats[0])):
        statted_image.text(
            (70, 820 + i * 80), major_stats[0][i], font=large_stat_font, fill=white
        )

    for i in range(0, len(major_stats[1])):
        if i == 0:
            if major_stats[1][i] == "None":
                major_stats[1][i] = "-"
            statted_image.text(
                (650 - word.calc_length(major_stats[1][i], 60), 820 + i * 80),
                major_stats[1][i],
                font=large_stat_font,
                fill=colour[0],
                stroke_fill=colour[1],
                stroke_width=1,
            )
        elif i == 1:
            if major_stats[1][i] != "None":
                rounded_rank = int(major_stats[1][i])
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
                major_stats[1][i] = "#" + major_stats[1][i]
            else:
                major_stats[1][i] = "-"
                rounded_rank = 0
            statted_image.text(
                (650 - word.calc_length(major_stats[1][i], 60), 820 + i * 80),
                major_stats[1][i],
                font=large_stat_font,
                fill=rank_colour[rounded_rank],
            )
        elif i == 2:
            rounded_win_loss = float(major_stats[1][i])
            if rounded_win_loss < 0.8:
                rounded_win_loss = 0
            elif rounded_win_loss < 1:
                rounded_win_loss = 1
            elif rounded_win_loss < 1.2:
                rounded_win_loss = 2
            elif rounded_win_loss < 1.5:
                rounded_win_loss = 3
            elif rounded_win_loss < 2:
                rounded_win_loss = 4
            elif rounded_win_loss >= 2:
                rounded_win_loss = 5
            statted_image.text(
                (650 - word.calc_length(major_stats[1][i], 60), 820 + i * 80),
                major_stats[1][i],
                font=large_stat_font,
                fill=ws_colour[rounded_win_loss],
            )
        elif i == 3:
            if not major_stats[1][i]:
                major_stats[1][i] = "-"
                rounded_pb = 0
            else:
                real_pb = response["statistics"]["total"]["bestTime"]["ranked"]
                rounded_pb = rank.get_rank(rank.get_elo_equivalent(real_pb, "pb"))

            pb_colours = rank.get_colour(elos[rounded_pb])
            statted_image.text(
                (650 - word.calc_length(major_stats[1][i], 60), 820 + i * 80),
                major_stats[1][i],
                font=large_stat_font,
                fill=pb_colours[0],
                stroke_fill=pb_colours[1],
                stroke_width=1,
            )
        else:
            statted_image.text(
                (650 - word.calc_length(major_stats[1][i], 60), 820 + i * 80),
                major_stats[1][i],
                font=large_stat_font,
                fill=white,
            )

    return card


def get_season_stats(response):
    wins = str(response["statistics"]["season"]["wins"]["ranked"])
    losses = str(response["statistics"]["season"]["loses"]["ranked"])
    plays = str(response["statistics"]["season"]["playedMatches"]["ranked"])
    draws = str(int(plays) - int(wins) - int(losses))
    best_elo = str(response["seasonResult"]["highest"])
    ff_loss = str(games.get_ff_loss(response, "season"))
    avg_completion = numb.digital_time(games.get_avg_completion(response, "season"))

    return [
        ["W/L/D:", "Best ELO:", "FF/loss:", "Avg Finish:"],
        [f"{wins}/{losses}/{draws}", best_elo, ff_loss, avg_completion],
    ]


def get_lifetime_stats(response):
    playtime = str(games.get_playtime(response, "total"))
    playtime_day = str(games.get_playtime_day(response))
    plays = str(response["statistics"]["total"]["playedMatches"]["ranked"])
    best_ws = str(response["statistics"]["total"]["highestWinStreak"]["ranked"])

    return [
        ["Playtime:", "PTime/day:", "Games:", "Best WS:"],
        [f"{playtime} h", f"{playtime_day} m", plays, best_ws],
    ]


def get_major_stats(response):
    elo = str(response["eloRate"])
    ranking = str(response["eloRank"])
    win_loss = str(
        round(
            response["statistics"]["season"]["wins"]["ranked"]
            / max(response["statistics"]["season"]["loses"]["ranked"], 1),
            2,
        )
    )
    pb = response["statistics"]["total"]["bestTime"]["ranked"]
    if pb:
        pb = numb.digital_time(pb)

    return [["ELO:", "Rank:", "Win/loss:", "PB:"], [elo, ranking, win_loss, pb]]
