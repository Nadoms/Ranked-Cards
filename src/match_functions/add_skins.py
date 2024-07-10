import requests
from io import BytesIO
from os import path

from PIL import Image


def write(chart, uuids):
    middle = 600
    x_values = [middle-220, middle+220]
    y_values = [100, 275]

    for i in range(0, 2):
        skin = get_skin(uuids[i], i)
        x = int(x_values[i] + (i-1) * skin.size[0])
        chart.paste(skin, (x, y_values[i]), skin)
    return chart


def get_skin(uuid, i):
    mid = 35
    turn = 30
    yaws = [mid+turn, mid-turn]
    try:
        yaw = yaws[i]
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.'}
        response = requests.get(f"https://visage.surgeplay.com/head/250/{uuid}?y={yaw}&p=15", headers=headers, timeout=10)
        skin = Image.open(BytesIO(response.content))
    except:
        skin = get_default_skin(i)
    return skin


def get_default_skin(i):
    right_left = ["r", "l"]
    file = path.join("src", "pics", "other", f"{right_left[i]}small_default_head.webp")
    skin = Image.open(file)
    return skin
