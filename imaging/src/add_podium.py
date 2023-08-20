from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
import requests

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
    
    podium = Image.open(fr"C:\Users\Ntakr\VSCode\Ranked-Cards\imaging\src\pics\podiums\podium_{tier}.webp")
    podium = podium.resize((round(podium.size[0]*1.3), round(podium.size[1]*1.3)))
    return podium

def get_border():
    
    border = Image.open(fr"C:\Users\Ntakr\VSCode\Ranked-Cards\imaging\src\pics\podiums\podium_bg.webp")
    border = border.resize((round(border.size[0]*1.4), round(border.size[1]*1.4)))
    return border