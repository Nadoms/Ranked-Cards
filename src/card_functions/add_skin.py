from PIL import Image
import requests
from io import BytesIO
from os import path

def write(card, uuid):
    skin = get_skin(uuid)
    card.paste(skin, (round(960-skin.size[0]/2), 230), skin)
    return card

def get_skin(uuid):
    try:
        response = requests.get(f"https://visage.surgeplay.com/full/832/{uuid}?y=20&p=0")
        skin = Image.open(BytesIO(response.content))
    except:
        skin = get_default_skin()
    skin = skin.resize((round(skin.size[0]*0.85), round(skin.size[1]*0.85)))
    return skin

def get_default_skin():
    file = path.join("src", "pics", "other", "default_skin.webp")
    skin = Image.open(file)
    return skin