import src.add_boxes
import src.add_name
import src.add_stats
import src.add_podium
import src.add_skin
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pathlib import Path

folder = Path(r"C:\Users\Ntakr\VSCode\Ranked-Cards\imaging\src\pics")
bg = "dirt.jpg"
name = "RED_LIME"
card = Image.open(folder / bg)
src.add_boxes.write(card, name)
src.add_name.write(card, name)
src.add_stats.write(card, name)
src.add_podium.write(card, name)
src.add_skin.write(card, name)