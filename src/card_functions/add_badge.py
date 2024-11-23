from os import path

from PIL import Image, ImageDraw, ImageFont

from gen_functions import rank, word


def write(card, response):
    badge = get_badge(response)
    dim = badge.size[0]

    x = 190
    y = 500
    circled_image = ImageDraw.Draw(card)

    circled_image.ellipse(
        [
            round(x - dim * 0.7),
            round(y - dim * 0.7),
            round(x + dim * 0.7),
            round(y + dim * 0.7),
        ],
        outline=rank.get_colour(response["eloRate"])[2],
        width=8,
    )

    if response["eloRate"] and response["eloRate"] >= 2000:
        circled_image.ellipse(
            [
                round(x - dim * 0.7),
                round(y - dim * 0.7),
                round(x + dim * 0.7),
                round(y + dim * 0.7),
            ],
            outline=rank.get_colour(response["eloRate"])[1],
            width=8,
        )
    else:
        circled_image.arc(
            [
                round(x - dim * 0.7),
                round(y - dim * 0.7),
                round(x + dim * 0.7),
                round(y + dim * 0.7),
            ],
            fill=rank.get_colour(response["eloRate"])[0],
            width=8,
            start=270,
            end=rank.get_degree(response["eloRate"]),
        )

    circled_image.ellipse(
        [
            round(x - dim * 0.66),
            round(y - dim * 0.66),
            round(x + dim * 0.66),
            round(y + dim * 0.66),
        ],
        outline="#ffffff",
        width=7,
    )

    circled_image.ellipse(
        [
            round(x - dim * 0.66),
            round(y - dim * 0.66),
            round(x + dim * 0.66),
            round(y + dim * 0.66),
        ],
        outline="#000000",
        width=4,
    )

    card.paste(badge, (round(x - dim / 2), round(y - dim / 2)), badge)

    tier = get_tier(response)
    x = 555
    y = 475
    rank_size = 80
    division_size = 140
    if tier[0] == "Netherite" or tier[0] == "Unranked":
        y += 65
        rank_size -= 10

    rank_shadow_font = ImageFont.truetype("minecraft_font.ttf", rank_size - 5)
    division_shadow_font = ImageFont.truetype("minecraft_font.ttf", division_size - 10)
    rank_font = ImageFont.truetype("minecraft_font.ttf", rank_size)
    division_font = ImageFont.truetype("minecraft_font.ttf", division_size)

    ranked_image = ImageDraw.Draw(card)
    ranked_image.text(
        (x - word.calc_length(tier[0], rank_size - 5) / 2, y - rank_size - 5),
        tier[0],
        font=rank_shadow_font,
        fill="#000000",
        stroke_width=3,
    )
    ranked_image.text(
        (x - word.calc_length(tier[1], division_size - 10) / 2, y),
        tier[1],
        font=division_shadow_font,
        fill="#000000",
        stroke_width=3,
    )
    ranked_image.text(
        (x - word.calc_length(tier[0], rank_size) / 2, y - 20 - rank_size),
        tier[0],
        font=rank_font,
        fill=rank.get_colour(response["eloRate"])[0],
        stroke_fill=rank.get_colour(response["eloRate"])[1],
        stroke_width=4,
    )
    ranked_image.text(
        (x - word.calc_length(tier[1], division_size) / 2, y - 20),
        tier[1],
        font=division_font,
        fill=rank.get_colour(response["eloRate"])[0],
        stroke_fill=rank.get_colour(response["eloRate"])[1],
        stroke_width=4,
    )

    return card


def get_badge(response):
    elo = response["eloRate"]
    tier = rank.get_rank(elo)

    file = path.join("src", "pics", "ranks", f"rank_{tier}.png")
    badge = Image.open(file)
    badge = badge.resize(
        (round(badge.size[0] * 14), round(badge.size[1] * 14)), resample=Image.NEAREST
    )
    return badge


def get_tier(response):
    elo = response["eloRate"]
    ranks = ["Coal", "Iron", "Gold", "Emerald", "Diamond", "Netherite", "Unranked"]

    tier = [ranks[rank.get_rank(elo)], rank.get_division(elo)]

    return tier
