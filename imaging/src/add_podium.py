from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests
from io import BytesIO

from . import rank

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]

    podium = get_podium(response)
    card.paste(podium, (round(960-podium.size[0]/2), 800), podium)
    return card

def get_podium(response):
    rank = get_rank(response)
    
    podium = Image.open(fr"C:\Users\Ntakr\VSCode\Ranked-Cards\imaging\src\pics\podium_{rank}.webp")
    podium = podium.resize((round(podium.size[0]*1.3), round(podium.size[1]*1.3)))
    return podium

def get_rank(response):
    elo = response["elo_rate"]
    return rank.get_podium(elo)