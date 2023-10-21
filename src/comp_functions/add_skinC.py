from PIL import Image
import requests
from io import BytesIO

def write(card, uuid):
    skin = get_skin(uuid)
    card.paste(skin, (round(960-skin.size[0]/2), 230), skin)
    return card

def get_skin(uuid):
    response = requests.get(f"https://visage.surgeplay.com/full/832/{uuid}?y=20&p=0")
    skin = Image.open(BytesIO(response.content))
    skin = skin.resize((round(skin.size[0]*0.85), round(skin.size[1]*0.85)))
    return skin