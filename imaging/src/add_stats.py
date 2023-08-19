from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from . import word_length
import requests

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]
    statted_image = ImageDraw.Draw(card)
    stat_font = ImageFont.truetype('minecraft_font.ttf', 40)
    large_stat_font = ImageFont.truetype('minecraft_font.ttf', 60)

    season_stats = get_season_stats(response)

    statted_image.text((1350, 50), "Season Stats", font=large_stat_font, fill=(255, 255, 255))
    for i in range(0, len(season_stats[0])):
        statted_image.text((1350, 140+i*60), season_stats[0][i], font=stat_font, fill=(255, 255, 255))

    for i in range(0, len(season_stats[1])):
        statted_image.text((1827-word_length.calc_length(season_stats[1][i], 40), 140+i*60), season_stats[1][i], font=stat_font, fill=(255, 255, 255))

    lifetime_stats = get_lifetime_stats(response)

    statted_image.text((1350, 500), "Lifetime Stats", font=large_stat_font, fill=(255, 255, 255))
    for i in range(0, len(lifetime_stats[0])):
        statted_image.text((1350, 590+i*60), lifetime_stats[0][i], font=stat_font, fill=(255, 255, 255))

    for i in range(0, len(lifetime_stats[1])):
        statted_image.text((1827-word_length.calc_length(lifetime_stats[1][i], 40), 590+i*60), lifetime_stats[1][i], font=stat_font, fill=(255, 255, 255))

    major_stats = get_major_stats(response)

    for i in range(0, len(major_stats[0])):
        statted_image.text((70, 820+i*80), major_stats[0][i], font=large_stat_font, fill=(255, 255, 255))
    
    for i in range(0, len(major_stats[1])):
        statted_image.text((650-word_length.calc_length(major_stats[1][i], 60), 820+i*80), major_stats[1][i], font=large_stat_font, fill=(255, 255, 255))

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
    games = str(response["total_played"])
    best_elo = str(response["best_elo_rate"])
    forfeit_loss = str("N/A")
    playtime = str("N/A")

    return [["Games:",
             "Best ELO:",
             "FF/loss:",
             "Playtime:"],
            [games,
             best_elo,
             forfeit_loss,
             f"{playtime}h"]]

def get_major_stats(response):
    elo = str(response["elo_rate"])
    rank = str(response["elo_rank"])
    win_loss = str(response["records"]["2"]["win"] / response["records"]["2"]["lose"])
    pb = str(response["best_record_time"])

    return [["Elo:",
             "Rank:",
             "Win/loss:",
             "PB:"],
            [elo,
             f"#{rank}",
             win_loss,
             pb]]