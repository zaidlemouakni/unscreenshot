"""Enlarged crop of the source with a coordinate grid, to read small text or confirm a position by eye.

    python scripts/crop.py work/source.png <x0> <y0> <x1> <y1> [--zoom 4] [--grid 10] [--out work/crop.png]

Grid lines every --grid source pixels (a stronger line and a label every 5 lines). Coordinates in labels
are source pixels, the same system as analysis.json and spec.json.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ui_font  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image')
    ap.add_argument('box', nargs=4, type=int)
    ap.add_argument('--zoom', type=float, default=4)
    ap.add_argument('--grid', type=int, default=10)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    x0, y0, x1, y1 = a.box
    src = Image.open(a.image).convert('RGB')
    z = a.zoom
    crop = src.crop((x0, y0, x1, y1)).resize((round((x1 - x0) * z), round((y1 - y0) * z)), Image.LANCZOS)
    if a.grid > 0:
        dr = ImageDraw.Draw(crop, 'RGBA')
        font = ui_font(12)
        gx = (x0 // a.grid + 1) * a.grid
        while gx < x1:
            strong = gx % (a.grid * 5) == 0
            X = (gx - x0) * z
            dr.line([(X, 0), (X, crop.height)], fill=(255, 0, 80, 110 if strong else 45), width=1)
            if strong:
                dr.text((X + 2, 1), str(gx), fill=(255, 0, 80, 255), font=font)
            gx += a.grid
        gy = (y0 // a.grid + 1) * a.grid
        while gy < y1:
            strong = gy % (a.grid * 5) == 0
            Y = (gy - y0) * z
            dr.line([(0, Y), (crop.width, Y)], fill=(0, 120, 255, 110 if strong else 45), width=1)
            if strong:
                dr.text((2, Y + 1), str(gy), fill=(0, 90, 255, 255), font=font)
            gy += a.grid
    out = a.out or os.path.join(os.path.dirname(a.image), f'crop_{x0}_{y0}_{x1}_{y1}.png')
    crop.save(out)
    print(out, crop.size)


if __name__ == '__main__':
    main()
