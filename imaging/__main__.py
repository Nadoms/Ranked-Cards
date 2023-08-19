import src.add_boxes
import src.add_name
import src.add_stats
import src.add_podium
import src.add_skin

import requests
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pathlib import Path

folder = Path(r"C:\Users\Ntakr\VSCode\Ranked-Cards\imaging\src\pics")
bg = "dirt.jpg"
input_name = "nadoms"
response = requests.get(f"https://mcsrranked.com/api/users/{input_name}").json()
if response["status"] != "error":
    name = response["data"]["nickname"]
    card = Image.open(folder / bg)
    src.add_boxes.write(card, name)
    src.add_name.write(card, name)
    src.add_stats.write(card, name)
    src.add_podium.write(card, name)
    src.add_skin.write(card, name)
else:
    print("Player not found.")