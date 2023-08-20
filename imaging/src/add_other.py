from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# rank with a circle indicating how close to the next main rank, with lines for each division

def write(card, name):
    ranked_image = ImageDraw.Draw(card)
    
    return card