from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests

from . import rank

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]

    badge = get_badge(response)
    card.paste(badge, (round(960-badge.size[0]/2), 800), badge)
    return card

def get_badge(response):
    elo = response["elo_rate"]
    tier = rank.get_rank(elo)
    
    badge = Image.open(fr"C:\Users\Ntakr\VSCode\Ranked-Cards\imaging\src\pics\ranks\rank_{tier}.png")
    badge = badge.resize((round(badge.size[0]*20), round(badge.size[1]*20)), resample=Image.NEAREST)
    return badge