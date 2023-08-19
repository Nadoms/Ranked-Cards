from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from . import word_length

def write(card, name):
    boxed_image = ImageDraw.Draw(card)
    for box in get_boxes(name):
        boxed_image.rectangle(box, fill="#122b30", outline="#000000", width=15)
    #    statted_image.text((1350, 50), "Season Stats", font=large_stat_font, fill=(255, 255, 255))
    #    statted_image.text((1827-word_length.calc_length(season_stats[1][i], 40), 140+i*60), season_stats[1][i], font=stat_font, fill=(255, 255, 255))

    #    statted_image.text((1350, 500), "Lifetime Stats", font=large_stat_font, fill=(255, 255, 255))
    #    statted_image.text((1827-word_length.calc_length(lifetime_stats[1][i], 40), 590+i*60), lifetime_stats[1][i], font=stat_font, fill=(255, 255, 255))

    #    statted_image.text((70, 820+i*80), major_stats[0][i], font=large_stat_font, fill=(255, 255, 255))
    #    statted_image.text((650-word_length.calc_length(major_stats[1][i], 60), 820+i*80), major_stats[1][i], font=large_stat_font, fill=(255, 255, 255))

    return card

def get_boxes(name):
    boxes = [[1350, 50, 1827, 440], [1350, 500, 1827, 890], [70, 820, 650, 1140], get_name_box(name)]
    for box in boxes:
        box[0] -= 30
        box[1] -= 20
        box[2] += 30
        box[3] += 20
    return boxes

def get_name_box(name):
    box = [70, 50, 130+word_length.calc_length(name, 140), 305]
    return box