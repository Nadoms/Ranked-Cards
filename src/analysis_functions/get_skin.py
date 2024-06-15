from PIL import Image
import requests
from io import BytesIO
from os import path

def __init__(self, uuid):
    try:
        skin = get_skin(uuid)
    except:
        skin = get_default_skin()
    return skin

def get_skin(uuid):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
    response = requests.get(f"https://visage.surgeplay.com/head/250/{uuid}?y=5&p=15", headers=headers)
    skin = Image.open(BytesIO(response.content))
    return skin

def get_default_skin():
    file = path.join("src", "pics", "other", "lsmall_default_head.webp")
    skin = Image.open(file)
    return skin