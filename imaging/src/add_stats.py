from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from . import word_length

def write(card, name):
    statted_image = ImageDraw.Draw(card)
    stat_font = ImageFont.truetype('minecraft_font.ttf', 40)
    large_stat_font = ImageFont.truetype('minecraft_font.ttf', 60)

    season_stats = get_season_stats()

    statted_image.text((1350, 50), "Season Stats", font=large_stat_font, fill=(255, 255, 255))
    for i in range(0, len(season_stats[0])):
        statted_image.text((1350, 140+i*60), season_stats[0][i], font=stat_font, fill=(255, 255, 255))

    for i in range(0, len(season_stats[1])):
        statted_image.text((1827-word_length.calc_length(season_stats[1][i], 40), 140+i*60), season_stats[1][i], font=stat_font, fill=(255, 255, 255))

    lifetime_stats = get_lifetime_stats()

    statted_image.text((1350, 500), "Lifetime Stats", font=large_stat_font, fill=(255, 255, 255))
    for i in range(0, len(lifetime_stats[0])):
        statted_image.text((1350, 590+i*60), lifetime_stats[0][i], font=stat_font, fill=(255, 255, 255))

    for i in range(0, len(lifetime_stats[1])):
        statted_image.text((1827-word_length.calc_length(lifetime_stats[1][i], 40), 590+i*60), lifetime_stats[1][i], font=stat_font, fill=(255, 255, 255))

    major_stats = get_major_stats()

    for i in range(0, len(major_stats[0])):
        statted_image.text((70, 820+i*80), major_stats[0][i], font=large_stat_font, fill=(255, 255, 255))
    
    for i in range(0, len(major_stats[1])):
        statted_image.text((650-word_length.calc_length(major_stats[1][i], 60), 820+i*80), major_stats[1][i], font=large_stat_font, fill=(255, 255, 255))

    return card

def get_season_stats():
    wins = str(30)
    draws = str(10)
    losses = str(10)
    games = str(50)
    best_elo = str(1300)
    forfeit_loss = "60%" # % of games lost which are forfeits
    playtime = str(107.4)

    return [["W/D/L:",
             "Games:",
             "Best ELO:",
             "FF/Loss:",
             "Playtime:"],
            [f"{wins}/{draws}/{losses}",
             games,
             best_elo,
             forfeit_loss,
             f"{playtime}h"]]

def get_lifetime_stats():
    wins = str(30)
    draws = str(10)
    losses = str(10)
    games = str(50)
    best_elo = str(1300)
    forfeit_loss = "60%" # % of games lost which are forfeits
    playtime = str(107.4)

    return [["W/D/L:",
             "Games:",
             "Best ELO:",
             "FF/Loss:",
             "Playtime:"],
            [f"{wins}/{draws}/{losses}",
             games,
             best_elo,
             forfeit_loss,
             f"{playtime}h"]]

def get_major_stats():
    elo = str(1250)
    rank = "#340"
    winrate = "55%"
    pb = "15m 8s"

    return [["Elo:",
             "Rank:",
             "Winrate:",
             "PB:"],
            [elo,
             rank,
             winrate,
             pb]]