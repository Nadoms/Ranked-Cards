from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests
from io import BytesIO

def write(card, name):
    podium = get_podium(name)
    card.paste(podium, (round(960-podium.size[0]/2), 800), podium)
    return card

def get_podium(name):
    rank = get_rank(name)
    
    podium = Image.open(fr"C:\Users\Ntakr\VSCode\Ranked-Cards\imaging\src\pics\podium_{rank}.webp")
    podium = podium.resize((round(podium.size[0]*1.3), round(podium.size[1]*1.3)))
    return podium

def get_rank(name):
    return 1