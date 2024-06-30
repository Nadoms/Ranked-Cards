from os import path
from PIL import Image, ImageDraw, ImageFont

img_size_x = 960
img_size_y = 760
line_margin = 100

def main(split_polygon, ow_polygon):
    
    polygons = Image.new('RGBA', (img_size_x * 2, img_size_y), (0, 0, 0, 255))
    polygons.paste(split_polygon, (0, 0), split_polygon)
    polygons.paste(ow_polygon, (img_size_x, 0), ow_polygon)

    polygons_draw = ImageDraw.Draw(polygons)

    xy = [img_size_x, line_margin, img_size_x, img_size_y-line_margin]
    polygons_draw.line(xy, fill="#000000", width=8)
    xy[1] += 3
    xy[3] -= 3
    polygons_draw.line(xy, fill="#ffffff", width=2)

    return polygons