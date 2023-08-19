import src.add_name as name
import src.add_stats as stats
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pathlib import Path

folder = Path(r"C:\Users\Ntakr\VSCode\Ranked-Stats\imaging\src\pics")
bg = "dirt.jpg"
card = Image.open(folder / bg)
name.write(card)
stats.write(card)