from PIL import Image
import requests
from os import path

from . import rank

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]

    podium = get_podium(response)
    border = get_border()
    card.paste(border, (round(960-border.size[0]/2), round(990-border.size[1]/2)), border)
    card.paste(podium, (round(960-podium.size[0]/2), round(990-podium.size[1]/2)), podium)
    return card

def get_podium(response):
    elo = response["elo_rate"]
    tier = rank.get_rank(elo)
    
    file = path.join("src", "pics", "podiums", f"podium_{tier}.webp")
    podium = Image.open(file)
    podium = podium.resize((round(podium.size[0]*1.3), round(podium.size[1]*1.3)))
    return podium

def get_border():
    file = path.join("src", "pics", "podiums", "podium_bg.webp")
    border = Image.open(file)
    border = border.resize((round(border.size[0]*1.38), round(border.size[1]*1.38)))
    return border