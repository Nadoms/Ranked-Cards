from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests

from . import rank

def write(card, name):
    response = requests.get(f"https://mcsrranked.com/api/users/{name}").json()["data"]

    badge = get_badge(response)
    dim = badge.size[0]

    x = 185
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

    return card

def get_badge(response):
    elo = response["elo_rate"]
    tier = rank.get_rank(elo)
    
    badge = Image.open(fr"C:\Users\Ntakr\VSCode\Ranked-Cards\imaging\src\pics\ranks\rank_{tier}.png")
    badge = badge.resize((round(badge.size[0]*14), round(badge.size[1]*14)), resample=Image.NEAREST)
    return badge