from PIL import ImageDraw, ImageFont

from gen_functions import word, rank

def write(analysis, uuids, response, vs_response):
    statted_image = ImageDraw.Draw(analysis)
    stat_size = 30
    stat_font = ImageFont.truetype('minecraft_font.ttf', stat_size)
    x_values = [900, 1020]
    y_values = [250, 320, 390]

    scores = get_scores(uuids, vs_response)

    for i in range(0, 2):
        stats = get_stats(response, scores, uuids, i)
        legacy_elo_colour = rank.get_colour(int(stats[0]))[0]
        current_elo_colour = rank.get_colour(int(stats[1]))[0]
        score_colour = "#00ffff"
        colours = [legacy_elo_colour, current_elo_colour, score_colour]

        for j in range(len(stats)):
            x = int(x_values[i] + (i-1) * word.calc_length(stats[j], stat_size))
            y = y_values[j] - int(word.horiz_to_vert(stat_size) / 2)

            statted_image.text((x, y), stats[j], font=stat_font, fill=colours[j])
        
    return analysis

def get_stats(response, scores, uuids, i):
    current_elo = str(response["members"][i]["elo_rate"])
    for score_change in response["score_changes"]:
        if score_change["uuid"] == uuids[i]:
            legacy_elo = str(score_change["score"])

    return [legacy_elo, current_elo, scores[i]]

def get_scores(uuids, vs_response):
    scores = []
    for uuid in uuids:
        score = 0
        for season in vs_response["win_count"]:
            score += vs_response["win_count"][season][uuid]
        scores.append(str(score))

    return scores