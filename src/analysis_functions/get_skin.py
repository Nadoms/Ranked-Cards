from PIL import Image
import requests
from io import BytesIO
from os import path

def main(uuid):
    try:
        skin = f"https://visage.surgeplay.com/head/250/{uuid}?y=5&p=15"
        response = requests.get(skin)
    except:
        skin = "https://cdn.discordapp.com/attachments/818965226291593268/1258028009718550618/lsmall_default_head.webp"
    return skin