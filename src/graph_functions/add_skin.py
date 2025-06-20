from os import path
from io import BytesIO

import requests
from PIL import Image


def write(graph, uuid):
    skin = get_skin(uuid)
    graph.paste(skin, (0, 0), skin)
    return graph


def get_skin(uuid):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0."
        }
        response = requests.get(
            f"https://visage.surgeplay.com/head/120/{uuid}?y=65&p=15",
            headers=headers,
            timeout=2,
        )
        skin = Image.open(BytesIO(response.content))
    except:
        skin = get_default_skin()
    return skin


def get_default_skin():
    file = path.join("src", "pics", "other", "default_head.webp")
    skin = Image.open(file)
    return skin
