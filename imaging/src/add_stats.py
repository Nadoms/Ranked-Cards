from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests

from . import word
from . import rank

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]

    statted_image = ImageDraw.Draw(card)
    stat_font = ImageFont.truetype('minecraft_font.ttf', 40)
    large_stat_font = ImageFont.truetype('minecraft_font.ttf', 60)
    colour = rank.get_colour(response["elo_rate"])
    best_colour = rank.get_colour(response["best_elo_rate"])
    white = "#ffffff"

    # Season stats
    season_stats = get_season_stats(response)

    statted_image.text((1350, 50), "Season Stats", font=large_stat_font, fill=white)
    for i in range(0, len(season_stats[0])):
        statted_image.text((1350, 140+i*60), season_stats[0][i], font=stat_font, fill=white)

    for i in range(0, len(season_stats[1])):
        statted_image.text((1827-word.calc_length(season_stats[1][i], 40), 140+i*60), season_stats[1][i], font=stat_font, fill=white)

    # Lifetime stats
    lifetime_stats = get_lifetime_stats(response)

    statted_image.text((1350, 500), "Lifetime Stats", font=large_stat_font, fill=white)
    for i in range(0, len(lifetime_stats[0])):
        statted_image.text((1350, 590+i*60), lifetime_stats[0][i], font=stat_font, fill=white)

    for i in range(0, len(lifetime_stats[1])):
        if i == 0:
            statted_image.text((1827-word.calc_length(lifetime_stats[1][i], 40), 590+i*60), lifetime_stats[1][i], font=stat_font, fill=best_colour[0], stroke_fill=best_colour[1], stroke_width=1)
        else:
            statted_image.text((1827-word.calc_length(lifetime_stats[1][i], 40), 590+i*60), lifetime_stats[1][i], font=stat_font, fill=white)

    # Major stats
    major_stats = get_major_stats(response)

    for i in range(0, len(major_stats[0])):
        statted_image.text((70, 820+i*80), major_stats[0][i], font=large_stat_font, fill=white)

    for i in range(0, len(major_stats[1])):
        if i == 0:
            statted_image.text((650-word.calc_length(major_stats[1][i], 60), 820+i*80), major_stats[1][i], font=large_stat_font, fill=colour[0], stroke_fill=colour[1], stroke_width=1)
        else:
            statted_image.text((650-word.calc_length(major_stats[1][i], 60), 820+i*80), major_stats[1][i], font=large_stat_font, fill=white)

    return card

def get_season_stats(response):
    wins = str(response["records"]["2"]["win"])
    losses = str(response["records"]["2"]["lose"])
    draws = str(response["records"]["2"]["draw"])
    games = str(response["season_played"])
    forfeit_loss = str("N/A")
    playtime = str("N/A")

    return [["W/L/D:",
             "Games:",
             "FF/Loss:",
             "Playtime:"],
            [f"{wins}/{losses}/{draws}",
             games,
             forfeit_loss,
             f"{playtime}h"]]

def get_lifetime_stats(response):
    wins = str("N/A")
    losses = str("N/A")
    draws = str("N/A")
    best_elo = str(response["best_elo_rate"])
    games = str(response["total_played"])
    forfeit_loss = str("N/A")
    playtime = str("N/A")

    return [["Best ELO:",
             "Games:",
             "FF/loss:",
             "Playtime:"],
            [best_elo,
             games,
             forfeit_loss,
             f"{playtime}h"]]

def get_major_stats(response):
    elo = str(response["elo_rate"])
    rank = str(response["elo_rank"])
    try:
        win_loss = str(round(response["records"]["2"]["win"] / response["records"]["2"]["lose"], 2))
    except:
        win_loss = str(response["records"]["2"]["win"])
    pb = str(response["best_record_time"])

    return [["Elo:",
             "Rank:",
             "Win/loss:",
             "PB:"],
            [elo,
             f"#{rank}",
             win_loss,
             pb]]