from PIL import Image, ImageDraw

IMG_SIZE_X = 960
IMG_SIZE_Y = 760
LINE_MARGIN = 100


def main(split_polygon, ow_polygon):
    polygons = Image.new('RGBA', (IMG_SIZE_X * 2, IMG_SIZE_Y), (0, 0, 0, 255))
    polygons.paste(split_polygon, (0, 0), split_polygon)
    polygons.paste(ow_polygon, (IMG_SIZE_X, 0), ow_polygon)

    polygons_draw = ImageDraw.Draw(polygons)

    xy = [IMG_SIZE_X, LINE_MARGIN, IMG_SIZE_X, IMG_SIZE_Y-LINE_MARGIN]
    polygons_draw.line(xy, fill="#000000", width=8)
    xy[1] += 3
    xy[3] -= 3
    polygons_draw.line(xy, fill="#ffffff", width=2)

    return polygons
