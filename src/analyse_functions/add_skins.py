from PIL import Image
import requests
from io import BytesIO
from os import path

def write(analysis, uuids):
    x_values = [910, 1010]
    for i in range(0, 2):
        skin = get_skin(uuids[i], i)
        x = int(x_values[i] + (i-1) * skin.size[0])
        y = 105
        analysis.paste(skin, (x, y), skin)
    return analysis

def get_skin(uuid, i):
    mid = 35
    turn = 30
    yaws = [mid+turn, mid-turn]
    try:
        yaw = yaws[i]
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
        response = requests.get(f"https://visage.surgeplay.com/head/250/{uuid}?y={yaw}&p=15", headers=headers)
        skin = Image.open(BytesIO(response.content))
    except:
        skin = get_default_skin()
    return skin

def get_default_skin():
    file = path.join("src", "pics", "other", "default_head.webp")
    skin = Image.open(file)
    return skin