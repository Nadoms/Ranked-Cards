import requests


def main(uuid):
    try:
        skin = f"https://visage.surgeplay.com/head/250/{uuid}?y=5&p=15"
        requests.get(skin, timeout=2)
    except:
        skin = "https://cdn.discordapp.com/attachments/818965226291593268/1258028009718550618/lsmall_default_head.webp"
    return skin
