from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests
from io import BytesIO

def write(card, name):
    skin = get_skin(name)
    card.paste(skin, (round(960-skin.size[0]/2), 260), skin)
    card.show()
    return card

def get_skin(name):
    response = requests.get(f"https://mc-heads.net/body/{name}")
    skin = Image.open(BytesIO(response.content))
    skin = skin.resize((round(skin.size[0]*1.6), round(skin.size[1]*1.6)))
    return skin