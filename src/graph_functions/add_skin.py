from os import path
from io import BytesIO

import requests
from PIL import Image

from rankedutils import constants


def write(graph, uuid):
    skin = get_skin(uuid)
    graph.paste(skin, (0, 0), skin)
    return graph


def get_skin(uuid):
    try:
        headers = {
            "User-Agent": constants.USER_AGENT
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
