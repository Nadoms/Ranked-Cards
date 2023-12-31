import math
from PIL import ImageDraw, ImageFont
import requests
from datetime import timedelta

from gen_functions import word, rank, match

def write(card, matches, uuid, response):
    statted_image = ImageDraw.Draw(card)
    stat_font = ImageFont.truetype('minecraft_font.ttf', 40)
    large_stat_font = ImageFont.truetype('minecraft_font.ttf', 60)

    colour = rank.get_colour(response["elo_rate"])
    best_colour = rank.get_colour(response["best_elo_rate"])
    rank_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#0f52ba", "#cd7f32", "#c0c0c0", "#ffd700"]
    win_loss_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#0f52fa", "#ffd700"]
    pb_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#0f52fa", "#ffd700"]
    avg_completion_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#0f52fa", "#ffd700"]
    ff_loss_colour = ["#bb3030", "#ff6164", "#86b8db", "#50fe50", "#0f52fa", "#ffd700"]
    ws_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#0f52fa", "#ffd700"]
    best_ws_colour = ["#888888", "#b3c4c9", "#86b8db", "#50fe50", "#0f52fa", "#ffd700"]
    w_d_l_colour = ["#86b8db", "#ee4b2b", "#ffbf00"]
    white = "#ffffff"

    # Season stats
    season_stats = get_season_stats(response, matches, uuid)

    statted_image.text((1350, 50), "Season Stats", font=large_stat_font, fill=white)
    for i in range(0, len(season_stats[0])):
        statted_image.text((1350, 140+i*60), season_stats[0][i], font=stat_font, fill=white)

    for i in range(0, len(season_stats[1])):
        if i == 0:
            w_d_l_spliced = season_stats[1][i].split("/")
            letters_placed = ""
            for j in range(0, len(w_d_l_spliced)):
                statted_image.text((1827-word.calc_length(season_stats[1][i], 40)+word.calc_length(letters_placed, 40), 140+i*60), w_d_l_spliced[j], font=stat_font, fill=w_d_l_colour[j])
                letters_placed += w_d_l_spliced[j]
                if j != len(w_d_l_spliced)-1:
                    statted_image.text((1827-word.calc_length(season_stats[1][i], 40)+word.calc_length(letters_placed, 40), 140+i*60), "/", font=stat_font, fill=white)
                    letters_placed += "/"
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
            statted_image.text((1827-word.calc_length(season_stats[1][i], 40), 140+i*60), season_stats[1][i], font=stat_font, fill=ff_loss_colour[rounded_ff_loss])
        elif i == 3:
            if season_stats[1][i] == ":00":
                season_stats[1][i] = "-"
                rounded_avg_completion = -1
            else:
                rounded_avg_completion = int(season_stats[1][i].split(":")[0])
            if rounded_avg_completion >= 26:
                rounded_avg_completion = 0
            elif rounded_avg_completion >= 21:
                rounded_avg_completion = 1
            elif rounded_avg_completion >= 17:
                rounded_avg_completion = 2
            elif rounded_avg_completion >= 15:
                rounded_avg_completion = 3
            elif rounded_avg_completion >= 13:
                rounded_avg_completion = 4
            elif rounded_avg_completion >= 7:
                rounded_avg_completion = 5
            else:
                rounded_avg_completion = 0
            statted_image.text((1827-word.calc_length(season_stats[1][i], 40), 140+i*60), season_stats[1][i], font=stat_font, fill=avg_completion_colour[rounded_avg_completion])
        else:
            statted_image.text((1827-word.calc_length(season_stats[1][i], 40), 140+i*60), season_stats[1][i], font=stat_font, fill=white)

    # Lifetime stats
    lifetime_stats = get_lifetime_stats(response, matches, uuid)

    statted_image.text((1350, 540), "Lifetime Stats", font=large_stat_font, fill=white)
    for i in range(0, len(lifetime_stats[0])):
        statted_image.text((1350, 630+i*60), lifetime_stats[0][i], font=stat_font, fill=white)

    for i in range(0, len(lifetime_stats[1])):
        if i == 0:
            statted_image.text((1827-word.calc_length(lifetime_stats[1][i], 40), 630+i*60), lifetime_stats[1][i], font=stat_font, fill=best_colour[0], stroke_fill=best_colour[1], stroke_width=1)
        elif i == 2:
            rounded_best_ws = min(math.floor(int(lifetime_stats[1][i])/2), len(best_ws_colour)-1)
            lifetime_stats[1][i] += " wins"
            statted_image.text((1827-word.calc_length(lifetime_stats[1][i], 40), 630+i*60), lifetime_stats[1][i], font=stat_font, fill=best_ws_colour[rounded_best_ws])
        else:
            statted_image.text((1827-word.calc_length(lifetime_stats[1][i], 40), 630+i*60), lifetime_stats[1][i], font=stat_font, fill=white)

    # Major stats
    major_stats = get_major_stats(response)

    for i in range(0, len(major_stats[0])):
        statted_image.text((70, 820+i*80), major_stats[0][i], font=large_stat_font, fill=white)

    for i in range(0, len(major_stats[1])):
        if i == 0:
            statted_image.text((650-word.calc_length(major_stats[1][i], 60), 820+i*80), major_stats[1][i], font=large_stat_font, fill=colour[0], stroke_fill=colour[1], stroke_width=1)
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
            statted_image.text((650-word.calc_length(major_stats[1][i], 60), 820+i*80), major_stats[1][i], font=large_stat_font, fill=rank_colour[rounded_rank])
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
            statted_image.text((650-word.calc_length(major_stats[1][i], 60), 820+i*80), major_stats[1][i], font=large_stat_font, fill=win_loss_colour[rounded_win_loss])
        elif i == 3:
            if major_stats[1][i] == ":00":
                major_stats[1][i] = "-"
                rounded_pb = -1
            else:
                rounded_pb = int(major_stats[1][i].split(":")[0])
            if rounded_pb >= 20:
                rounded_pb = 0
            elif rounded_pb >= 15:
                rounded_pb = 1
            elif rounded_pb >= 12:
                rounded_pb = 2
            elif rounded_pb >= 10:
                rounded_pb = 3
            elif rounded_pb >= 9:
                rounded_pb = 4
            elif rounded_pb >= 6:
                rounded_pb = 5
            else:
                rounded_pb = 0
            statted_image.text((650-word.calc_length(major_stats[1][i], 60), 820+i*80), major_stats[1][i], font=large_stat_font, fill=pb_colour[rounded_pb])
        else:
            statted_image.text((650-word.calc_length(major_stats[1][i], 60), 820+i*80), major_stats[1][i], font=large_stat_font, fill=white)

    return card

def get_season_stats(response, matches, uuid):
    wins = str(response["records"]["2"]["win"])
    losses = str(response["records"]["2"]["lose"])
    draws = str(response["records"]["2"]["draw"])
    games = str(response["season_played"])
    ff_loss = str(match.get_ff_loss(matches, True, uuid, response["nickname"]))
    avg_completion = str(timedelta(milliseconds=match.get_avg_completion(matches, True, uuid, response)))[2:7].lstrip("0")
    playtime = str(match.get_playtime(matches, True))

    return [["W/L/D:",
             "Games:",
             "FF/loss:",
             "Avg Finish:",
             "Playtime:"],
            [f"{wins}/{losses}/{draws}",
             games,
             ff_loss,
             avg_completion,
             f"{playtime} h"]]

def get_lifetime_stats(response, matches, uuid):
    best_elo = str(response["best_elo_rate"])
    games = str(response["total_played"])
    best_ws = str(response["highest_winstreak"])

    return [["Best ELO:",
             "Games:",
             "Best WS:"],
            [best_elo,
             games,
             best_ws]]

def get_major_stats(response):
    elo = str(response["elo_rate"])
    rank = str(response["elo_rank"])
    try:
        win_loss = str(round(response["records"]["2"]["win"] / response["records"]["2"]["lose"], 2))
    except:
        win_loss = str(response["records"]["2"]["win"])
    pb = str(timedelta(milliseconds=response["best_record_time"]))[2:7].lstrip("0")

    return [["Elo:",
             "Rank:",
             "Win/loss:",
             "PB:"],
            [elo,
             rank,
             win_loss,
             pb]]