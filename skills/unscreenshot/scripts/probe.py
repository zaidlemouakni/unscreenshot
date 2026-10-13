"""Precise point measurements on the source image (source pixels). Use it whenever a box, a colour or an
edge matters more than the automatic analysis gives.

    python scripts/probe.py work/source.png h <y> [x0 x1]      colour runs along a row (edges + colours)
    python scripts/probe.py work/source.png v <x> [y0 y1]      colour runs along a column
    python scripts/probe.py work/source.png color <x> <y> [r]  median colour of a (2r+1)^2 patch
    python scripts/probe.py work/source.png box <x> <y>        extent of the flat area containing (x, y)
    python scripts/probe.py work/source.png ink <x0> <y0> <x1> <y1>   ink box, cap/x-height band and baseline
                                                                  of the text inside that rectangle
Options: --tol 10 (colour tolerance for runs), --min 3 (shortest run reported).
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_rgb, rgb_to_hex  # noqa: E402


def runs(line, offset, tol, min_len):
    out, start, ref = [], 0, line[0].astype(int)
    for i in range(1, len(line)):
        if np.abs(line[i].astype(int) - ref).max() > tol:
            if i - start >= min_len:
                out.append((offset + start, offset + i, rgb_to_hex(np.median(line[start:i], axis=0))))
            start, ref = i, line[i].astype(int)
    if len(line) - start >= min_len:
        out.append((offset + start, offset + len(line), rgb_to_hex(np.median(line[start:], axis=0))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image')
    ap.add_argument('mode', choices=['h', 'v', 'color', 'box', 'ink'])
    ap.add_argument('args', nargs='*', type=float)
    ap.add_argument('--tol', type=int, default=10)
    ap.add_argument('--min', type=int, default=3)
    a = ap.parse_args()
    rgb = load_rgb(a.image)
    h, w = rgb.shape[:2]
    v = [int(round(x)) for x in a.args]
    if a.mode == 'h':
        y, x0, x1 = v[0], (v[1] if len(v) > 1 else 0), (v[2] if len(v) > 2 else w)
        for s, e, c in runs(rgb[y, x0:x1], x0, a.tol, a.min):
            print(f'x {s:>5} -> {e:>5}  ({e - s:>4} px)  {c}')
    elif a.mode == 'v':
        x, y0, y1 = v[0], (v[1] if len(v) > 1 else 0), (v[2] if len(v) > 2 else h)
        for s, e, c in runs(rgb[y0:y1, x], y0, a.tol, a.min):
            print(f'y {s:>5} -> {e:>5}  ({e - s:>4} px)  {c}')
    elif a.mode == 'color':
        x, y = v[0], v[1]
        r = v[2] if len(v) > 2 else 2
        patch = rgb[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1].reshape(-1, 3)
        print(rgb_to_hex(np.median(patch, axis=0)))
    elif a.mode == 'box':
        x, y = v[0], v[1]
        ref = np.median(rgb[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 3), axis=0)

        def same(px):
            return np.abs(px.astype(int) - ref).max() <= a.tol

        x0 = x
        while x0 > 0 and same(rgb[y, x0 - 1]):
            x0 -= 1
        x1 = x
        while x1 < w - 1 and same(rgb[y, x1 + 1]):
            x1 += 1
        y0 = y
        while y0 > 0 and same(rgb[y0 - 1, x]):
            y0 -= 1
        y1 = y
        while y1 < h - 1 and same(rgb[y1 + 1, x]):
            y1 += 1
        print(f'box [{x0}, {y0}, {x1 + 1}, {y1 + 1}]  ({x1 + 1 - x0} x {y1 + 1 - y0})  colour {rgb_to_hex(ref)}'
              '  (traverses only flat colour: a text or icon on the axis stops it early - probe again beside it)')
    elif a.mode == 'ink':
        x0, y0, x1, y1 = v[:4]
        sub = rgb[y0:y1, x0:x1].astype(int)
        border = np.concatenate([sub[0], sub[-1], sub[:, 0], sub[:, -1]])
        bg = np.median(border, axis=0)
        d = np.abs(sub - bg).max(axis=2)
        ink = d > max(40, 0.35 * d.max())
        ys, xs = np.nonzero(ink)
        if not len(ys):
            sys.exit('no ink found')
        rows = ink.sum(axis=1).astype(float)
        dense = np.flatnonzero(rows >= 0.5 * rows.max())
        light = np.flatnonzero(rows >= 0.08 * rows.max())
        strong = ink & (d >= np.percentile(d[ink], 70))
        col = np.median(sub[strong], axis=0)
        print(f'ink box [{x0 + xs.min()}, {y0 + ys.min()}, {x0 + xs.max() + 1}, {y0 + ys.max() + 1}]  '
              f'width {xs.max() + 1 - xs.min()}  cap_top {y0 + light[0]}  x_top {y0 + dense[0]}  '
              f'baseline {y0 + dense[-1] + 1}  colour {rgb_to_hex(col)}  background {rgb_to_hex(bg)}')


if __name__ == '__main__':
    main()
