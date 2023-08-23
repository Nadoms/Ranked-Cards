from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests

from . import rank
from . import word

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]

    badge = get_badge(response)
    dim = badge.size[0]

    x = 190
    y = 500
    circled_image = ImageDraw.Draw(card)
    circled_image.ellipse([round(x-dim*0.8),
                           round(y-dim*0.8),
                           round(x+dim*0.8),
                           round(y+dim*0.8)],
                           fill="#122b30",
                           outline="#000000",
                           width=12)
    
    circled_image.ellipse([round(x-dim*0.75),
                           round(y-dim*0.75),
                           round(x+dim*0.75),
                           round(y+dim*0.75)],
                           outline="#021b20",
                           width=5)
    
    circled_image.arc([round(x-dim*0.75),
                           round(y-dim*0.75),
                           round(x+dim*0.75),
                           round(y+dim*0.75)],
                           fill="#add8e6",
                           width=5,
                           start=270,
                           end=rank.get_degree(response["elo_rate"]))
    
    card.paste(badge, (round(x-dim/2), round(y-dim/2)), badge)

    tier = get_tier(response)
    y = 475
    rank_size = 80
    division_size = 140
    if tier[0] == "Netherite" or tier[0] == "Unranked":
        y += 65
        rank_size -=5


    rank_shadow_font = ImageFont.truetype('minecraft_font.ttf', rank_size-5)
    division_shadow_font = ImageFont.truetype('minecraft_font.ttf', division_size-10)
    rank_font = ImageFont.truetype('minecraft_font.ttf', rank_size)
    division_font = ImageFont.truetype('minecraft_font.ttf', division_size)
    
    ranked_image = ImageDraw.Draw(card)
    ranked_image.text((570-word.calc_length(tier[0], rank_size-5)/2, y-rank_size-5), tier[0], font=rank_shadow_font, fill="#000000", stroke_width=3)
    ranked_image.text((570-word.calc_length(tier[1], division_size-10)/2, y), tier[1], font=division_shadow_font, fill="#000000", stroke_width=3)
    ranked_image.text((570-word.calc_length(tier[0], rank_size)/2, y-20-rank_size), tier[0], font=rank_font, fill=rank.get_colour(response["elo_rate"])[0], stroke_fill=rank.get_colour(response["elo_rate"])[1], stroke_width=4)
    ranked_image.text((570-word.calc_length(tier[1], division_size)/2, y-20), tier[1], font=division_font, fill=rank.get_colour(response["elo_rate"])[0], stroke_fill=rank.get_colour(response["elo_rate"])[1], stroke_width=4)

    return card

def get_badge(response):
    elo = response["elo_rate"]
    tier = rank.get_rank(elo)
    
    badge = Image.open(fr"src\pics\ranks\rank_{tier}.png")
    badge = badge.resize((round(badge.size[0]*14), round(badge.size[1]*14)), resample=Image.NEAREST)
    return badge

def get_tier(response):
    elo = response["elo_rate"]
    ranks = ["Coal", "Iron", "Gold", "Emerald", "Diamond", "Netherite", "Unranked"]

    tier = [ranks[rank.get_rank(elo)], rank.get_division(elo)]

    return tier