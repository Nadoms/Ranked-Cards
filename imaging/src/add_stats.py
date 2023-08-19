from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from . import word_length

def write(card):
    statted_image = ImageDraw.Draw(card)
    stat_font = ImageFont.truetype('minecraft_font.ttf', 40)
    large_stat_font = ImageFont.truetype('minecraft_font.ttf', 60)

    minor_stats = get_minor_stats()

    statted_image.text((1200, 100), "Season Stats", font=large_stat_font, fill=(255, 255, 255))
    for i in range(0, len(minor_stats[0])):
        statted_image.text((1200, 190+i*60), minor_stats[0][i], font=stat_font, fill=(255, 255, 255))

    for i in range(0, len(minor_stats[1])):
        statted_image.text((1677-word_length.calc_length(minor_stats[1][i], 40), 190+i*60), minor_stats[1][i], font=stat_font, fill=(255, 255, 255))

    major_stats = get_major_stats()
    for i in range(0, len(major_stats)):
        statted_image.text((120, 900+i*80), major_stats[i], font=large_stat_font, fill=(255, 255, 255))

    card.show()
    return card

def get_minor_stats():
    wins = str(30)
    draws = str(10)
    losses = str(10)
    games = str(50)
    best_elo = str(1300)
    forfeit_loss = "60%" # % of games lost which are forfeits

    return [["W/D/L:",
             "Games:",
             "Best ELO:",
             "FF/Loss:"],
            [f"{wins}/{draws}/{losses}",
            games,
            best_elo,
            forfeit_loss]]

def get_major_stats():
    elo = str(1250)
    winrate = "55%"
    pb = "15m 8s"

    return [f"Elo: {elo}",
            f"Winrate: {winrate}",
            f"PB: {pb}"]