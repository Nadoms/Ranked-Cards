from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from . import word_length

def write(card, name):
    statted_image = ImageDraw.Draw(card)
    stat_font = ImageFont.truetype('minecraft_font.ttf', 40)
    large_stat_font = ImageFont.truetype('minecraft_font.ttf', 60)

    minor_stats = get_minor_stats()

    statted_image.text((1300, 100), "Season Stats", font=large_stat_font, fill=(255, 255, 255))
    for i in range(0, len(minor_stats[0])):
        statted_image.text((1300, 190+i*60), minor_stats[0][i], font=stat_font, fill=(255, 255, 255))

    for i in range(0, len(minor_stats[1])):
        statted_image.text((1777-word_length.calc_length(minor_stats[1][i], 40), 190+i*60), minor_stats[1][i], font=stat_font, fill=(255, 255, 255))

    major_stats = get_major_stats()

    for i in range(0, len(major_stats[0])):
        statted_image.text((70, 750+i*80), major_stats[0][i], font=large_stat_font, fill=(255, 255, 255))
    
    for i in range(0, len(major_stats[1])):
        statted_image.text((750-word_length.calc_length(major_stats[1][i], 60), 750+i*80), major_stats[1][i], font=large_stat_font, fill=(255, 255, 255))

    return card

def get_minor_stats():
    wins = str(30)
    draws = str(10)
    losses = str(10)
    games = str(50)
    best_elo = str(1300)
    forfeit_loss = "60%" # % of games lost which are forfeits
    playtime = "100 hours"

    return [["W/D/L:",
             "Games:",
             "Best ELO:",
             "FF/Loss:",
             "Playtime:"],
            [f"{wins}/{draws}/{losses}",
             games,
             best_elo,
             forfeit_loss,
             playtime]]

def get_major_stats():
    elo = str(1250)
    rank = "#340"
    tier = "Emerald 3"
    winrate = "55%"
    pb = "15m 8s"

    return [["Elo:",
             "Rank:",
             "Tier:",
             "Winrate:",
             "PB:"],
            [elo,
             rank,
             tier,
             winrate,
             pb]]