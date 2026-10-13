"""Measure a slide image: background, palette, filled regions (cards, bars, pills, circles), thin rules,
small marks (bullets, dots), graphics (icons, logos) and every text line (ink box, cap/x-height band,
baseline, colour). All coordinates are source pixels; boxes are edges [x0, y0, x1, y1] (x1/y1 exclusive).

    python scripts/analyze.py work/source.png --out work

Writes work/analysis.json, work/annotated.png (ids R#, L#, T#, G#, M# drawn on the slide) and
work/lines_1.png, lines_2.png... (every text line enlarged, with its id) for exact transcription.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (box_all, box_any, headline_metrics, label, load_rgb, local_background, objects,  # noqa: E402
                    rgb_to_hex, save_json, ui_font)


def palette(rgb, n=28, min_cov=0.06):
    """Flat colours by population: 5-bit histogram, greedy merge of close bins, median refinement."""
    q = (rgb >> 3).astype(np.int32)
    idx = (q[..., 0] << 10) | (q[..., 1] << 5) | q[..., 2]
    counts = np.bincount(idx.ravel(), minlength=1 << 15)
    total = float(idx.size)
    order = np.argsort(-counts)
    seeds = []
    for b in order[:400]:
        c = counts[b]
        if c < total * min_cov / 400:
            break
        col = np.array([(b >> 10) & 31, (b >> 5) & 31, b & 31], dtype=float) * 8 + 4
        for s in seeds:
            if np.abs(s['rgb'] - col).max() <= 12:
                s['n'] += c
                break
        else:
            seeds.append({'rgb': col, 'n': int(c)})
    img16 = rgb.astype(np.int16)
    out = []
    for s in sorted(seeds, key=lambda s: -s['n']):
        near = np.abs(img16 - s['rgb'].astype(np.int16)).max(axis=2) <= 10
        cnt = int(near.sum())
        if cnt < total * min_cov / 100:
            continue
        exact = np.median(rgb[near], axis=0)
        if any(np.abs(np.array(o['rgb']) - exact).max() <= 6 for o in out):
            continue
        out.append({'hex': rgb_to_hex(exact), 'rgb': [int(v) for v in exact], 'coverage': round(100 * cnt / total, 2)})
        if len(out) >= n:
            break
    return out


def corner_radius(sub):
    h, w = sub.shape
    m = int(max(2, min(min(h, w) // 2, 60)))
    rs = []
    for ys, xs in ((slice(0, m), slice(0, m)), (slice(0, m), slice(w - m, w)),
                   (slice(h - m, h), slice(0, m)), (slice(h - m, h), slice(w - m, w))):
        missing = float((~sub[ys, xs]).sum())
        rs.append(math.sqrt(missing / (1 - math.pi / 4)))
    return round(float(np.median(rs)), 1)


def find_regions(rgb, pal, width, height):
    """Solid fills (cards, bars, pills, circles, bands). An opening removes text strokes first, so text of
    a given colour never comes out as a 'region'; the fill ratio is measured on a closed mask."""
    out = []
    img16 = rgb.astype(np.int16)
    r = max(2, round(width / 450))
    for p in pal:
        if p['coverage'] < 0.1:
            continue
        col = np.array(p['rgb'], dtype=np.int16)
        mask = np.abs(img16 - col).max(axis=2) <= 12
        core = box_any(box_all(mask, r, r), r, r)
        closed = box_all(box_any(mask, r, r), r, r)
        lab, n = label(core)
        for i, x0, y0, x1, y1, cnt in objects(lab, n):
            w, h = x1 - x0 + 1, y1 - y0 + 1
            if cnt < 0.0003 * width * height or min(w, h) < 2 * r + 1 or w * h > 0.92 * width * height:
                continue
            sub = closed[y0:y1 + 1, x0:x1 + 1] & box_any(lab[y0:y1 + 1, x0:x1 + 1] == i, r, r)
            cnt = int(sub.sum())
            fill = cnt / float(w * h)
            if fill < 0.55:
                continue
            rad = corner_radius(sub)
            if 0.85 < w / h < 1.18 and 0.74 < fill < 0.83:
                shape = 'ellipse'
            elif fill >= 0.985 or rad < 1.5:
                shape = 'rect'
            elif rad >= 0.45 * min(w, h):
                shape = 'pill'
            elif fill > 0.86:
                shape = 'roundrect'
            else:
                shape = 'other'
            inner = (lab[y0:y1 + 1, x0:x1 + 1] == i) & mask[y0:y1 + 1, x0:x1 + 1]
            real = np.median(rgb[y0:y1 + 1, x0:x1 + 1][inner], axis=0) if inner.any() else col
            out.append({'box': [x0, y0, x1 + 1, y1 + 1], 'color': rgb_to_hex(real), 'fill_ratio': round(fill, 3),
                        'radius': rad, 'shape': shape, 'area': int(cnt), 'kind': 'fill'})
        # containers: frames of this colour around other content (cards with an inner panel, label boxes)
        if p['coverage'] >= 1.0:
            lab2, n2 = label(closed)
            for i, x0, y0, x1, y1, cnt in objects(lab2, n2):
                w, h = x1 - x0 + 1, y1 - y0 + 1
                if w * h < 0.004 * width * height or w * h > 0.92 * width * height:
                    continue
                sub = fill_holes(lab2[y0:y1 + 1, x0:x1 + 1] == i)
                fill = sub.sum() / float(w * h)
                if fill >= 0.8 and cnt / float(sub.sum()) < 0.85:
                    out.append({'box': [x0, y0, x1 + 1, y1 + 1], 'color': p['hex'], 'fill_ratio': round(fill, 3),
                                'radius': corner_radius(sub), 'shape': 'container', 'area': int(sub.sum()),
                                'kind': 'container'})
    out = dedupe(out)
    out.sort(key=lambda d: -d['area'])
    for k, d in enumerate(out, 1):
        d['id'] = f'R{k}'
    return out


def fill_holes(sub):
    try:
        from scipy import ndimage
        return ndimage.binary_fill_holes(sub)
    except Exception:
        lab, n = label(~sub)
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        holes = (lab > 0) & ~np.isin(lab, list(border))
        return sub | holes


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union else 0


def dedupe(regs):
    regs = sorted(regs, key=lambda d: (-d['fill_ratio'], -d['area']))
    kept = []
    for r in regs:
        if all(iou(r['box'], k['box']) < 0.8 for k in kept):
            kept.append(r)
    return kept


def merge_rules(rules, diff):
    """Join collinear fragments of the same rule; drop near-invisible ones."""
    rules = sorted(rules, key=lambda r: (r['h'] > r['w'], r['y0'] if r['w'] >= r['h'] else r['x0'], r['x0'], r['y0']))
    out = []
    for r in rules:
        horiz = r['w'] >= r['h']
        if out:
            p = out[-1]
            if horiz and p['w'] >= p['h'] and abs(p['y0'] - r['y0']) <= 1 and r['x0'] - p['x1'] <= 40:
                p['x1'], p['y1'] = max(p['x1'], r['x1']), max(p['y1'], r['y1'])
                p['w'], p['h'] = p['x1'] - p['x0'], p['y1'] - p['y0']
                continue
            if not horiz and p['h'] > p['w'] and abs(p['x0'] - r['x0']) <= 1 and r['y0'] - p['y1'] <= 40:
                p['x1'], p['y1'] = max(p['x1'], r['x1']), max(p['y1'], r['y1'])
                p['w'], p['h'] = p['x1'] - p['x0'], p['y1'] - p['y0']
                continue
        out.append(dict(r))
    keep = []
    for r in out:
        contrast = float(np.percentile(diff[r['y0']:r['y1'], r['x0']:r['x1']], 90))
        if contrast >= 14 and max(r['w'], r['h']) >= 60:
            keep.append(r)
    return keep


def line_metrics(sub_ink, y0):
    """Bands of a text line's row profile. 'baseline' is the bottom of the densest band: the real baseline for
    Latin, Cyrillic, Greek, Hebrew, Arabic and Thai; fit.py corrects it for scripts where the densest band sits
    elsewhere (the headline of Devanagari, the body of CJK). 'core' spans rows >= 30 % of the densest one: the
    letter bodies without the sparse marks above and below."""
    rows = sub_ink.sum(axis=1).astype(float)
    mx = rows.max()
    dense = np.flatnonzero(rows >= 0.5 * mx)
    light = np.flatnonzero(rows >= 0.08 * mx)
    core = np.flatnonzero(rows >= 0.3 * mx)
    base = int(y0 + dense[-1] + 1)
    return {'x_top': int(y0 + dense[0]), 'cap_top': int(y0 + light[0]), 'baseline': base,
            'core_top': int(y0 + core[0]), 'core_bottom': int(y0 + core[-1] + 1)}


def absorb_fragments(texts, marks):
    """Dots, accents and small pieces drawn apart from their letters (Arabic and Persian dots and vowel marks,
    Vietnamese and Thai marks, Devanagari signs, i-dots) belong to the text line they sit on, above or under:
    grow the line, drop the piece. Bullets stay marks: they sit beside the text, not over it.
    Returns (texts, marks) left."""
    alive = {id(t): t for t in texts}
    core = {id(t): (t['x0'], t['y0'], t['x1'], t['y1']) for t in texts}  # match on boxes before they grow

    def host(p, mark):
        cx, cy = (p['x0'] + p['x1']) / 2, (p['y0'] + p['y1']) / 2
        best = None
        for t in alive.values():
            x0, y0, x1, y1 = core[id(t)]
            h = y1 - y0
            # a text fragment is much shorter than its line and about one letter wide
            if t is p or (not mark and (h < 2.2 * p['h'] or p['w'] > 1.2 * h)):
                continue
            reach = 0.7 if mark else 0.5
            if x0 - 0.1 * h <= cx <= x1 + 0.1 * h and y0 - reach * h <= cy <= y1 + reach * h:
                d = abs(cy - (y0 + y1) / 2)
                if best is None or d < best[0]:
                    best = (d, t)
        return best[1] if best else None

    def grow(t, p):
        t['x0'], t['y0'] = min(t['x0'], p['x0']), min(t['y0'], p['y0'])
        t['x1'], t['y1'] = max(t['x1'], p['x1']), max(t['y1'], p['y1'])
        t['w'], t['h'] = t['x1'] - t['x0'], t['y1'] - t['y0']

    keep = []
    for m in marks:
        t = host(m, True)
        if t is None:
            keep.append(m)
        else:
            grow(t, m)
    for p in sorted(texts, key=lambda t: t['h']):
        if id(p) in alive:
            t = host(p, False)
            if t is not None:
                grow(t, p)
                del alive[id(p)]
    return [t for t in texts if id(t) in alive], keep


def merge_text(cands):
    cands = sorted(cands, key=lambda c: (c['y0'], c['x0']))
    changed = True
    while changed:
        changed = False
        for i in range(len(cands)):
            a = cands[i]
            if a is None:
                continue
            for j in range(i + 1, len(cands)):
                b = cands[j]
                if b is None:
                    continue
                ov = min(a['y1'], b['y1']) - max(a['y0'], b['y0'])
                hmin, hmax = min(a['h'], b['h']), max(a['h'], b['h'])
                gap = max(a['x0'], b['x0']) - min(a['x1'], b['x1'])
                inside = (a['y0'] <= b['y0'] and b['y1'] <= a['y1']) or (b['y0'] <= a['y0'] and a['y1'] <= b['y1'])
                dash = (a.get('bar') or b.get('bar')) and inside and 0 <= gap <= 0.3 * hmax
                # a short word inside the band of a tall one, one space away (Arabic "و", "في" next to a word
                # with alefs and descenders)
                word = inside and 0 <= gap <= 0.35 * hmax and hmin >= 0.25 * hmax
                # word spaces reach ~0.6 of the ink height in Korean (Malgun Gothic) and in spaced-out labels
                if ov >= 0.6 * hmin and gap <= 0.7 * hmax and (hmax <= 1.8 * hmin or dash or word):
                    for k in ('x0', 'y0'):
                        a[k] = min(a[k], b[k])
                    for k in ('x1', 'y1'):
                        a[k] = max(a[k], b[k])
                    a['w'], a['h'] = a['x1'] - a['x0'], a['y1'] - a['y0']
                    cands[j] = None
                    changed = True
        cands = [c for c in cands if c is not None]
    return cands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image')
    ap.add_argument('--out', default='work')
    ap.add_argument('--thr', type=int, default=42, help='ink contrast threshold vs local background (0-255)')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rgb = load_rgb(a.image)
    height, width = rgb.shape[:2]

    border = np.concatenate([rgb[:4].reshape(-1, 3), rgb[-4:].reshape(-1, 3),
                             rgb[:, :4].reshape(-1, 3), rgb[:, -4:].reshape(-1, 3)])
    bg = rgb_to_hex(np.median(border, axis=0))
    pal = palette(rgb)
    regions = find_regions(rgb, pal, width, height)

    bgl = local_background(rgb, max(4, round(width / 240)))
    diff = np.abs(rgb.astype(np.int16) - bgl).max(axis=2)

    # thin rules and separators, even very light ones (low threshold, no dilation)
    texts, rules, graphics, marks, bars = [], [], [], [], []
    lo = diff > 9
    lab, n = label(lo)
    rule_mask = np.zeros_like(lo)
    for i, x0, y0, x1, y1, cnt in objects(lab, n):
        w, h = x1 - x0 + 1, y1 - y0 + 1
        if (h <= max(4, height / 280) and w >= max(40, 10 * h)) or (w <= max(4, width / 500) and h >= max(40, 10 * w)):
            rules.append({'x0': x0, 'y0': y0, 'x1': x1 + 1, 'y1': y1 + 1, 'w': w, 'h': h, 'dens': 1.0})
            rule_mask[y0:y1 + 1, x0:x1 + 1] |= lab[y0:y1 + 1, x0:x1 + 1] == i

    rules = merge_rules(rules, diff)
    ink = (diff > a.thr) & ~rule_mask
    joined = box_any(ink, max(1, round(height / 900)), max(2, round(width / 330)))
    lab, n = label(joined)
    for i, x0, y0, x1, y1, cnt in objects(lab, n):
        sub = ink[y0:y1 + 1, x0:x1 + 1] & (lab[y0:y1 + 1, x0:x1 + 1] == i)
        ys, xs = np.nonzero(sub)
        if len(ys) < 4:
            continue
        tx0, tx1, ty0, ty1 = x0 + xs.min(), x0 + xs.max() + 1, y0 + ys.min(), y0 + ys.max() + 1
        w, h = tx1 - tx0, ty1 - ty0
        dens = len(ys) / float(w * h)
        c = {'x0': int(tx0), 'y0': int(ty0), 'x1': int(tx1), 'y1': int(ty1), 'w': int(w), 'h': int(h), 'dens': dens}
        if (w > 0.6 * width and h < max(8, height / 120)) or (h <= max(3, height / 350) and w >= max(25, 6 * h)) or \
                (w <= max(3, width / 600) and h >= max(25, 6 * w)):
            continue  # bands and edges of filled shapes: already covered by regions / rules
        elif max(w, h) <= max(10, width / 130) and 0.6 <= w / max(1, h) <= 1.6 and dens > 0.45:
            marks.append(c)  # bullet dots, small markers
        elif dens > 0.8 and h < max(10, height / 100) and w <= 8 * h:
            bars.append(c)  # dashes and minus signs: joined to the text they belong to below
        elif 5 <= h <= 0.11 * height and w >= 0.3 * h and 0.05 <= dens <= 0.8 and not (h > 18 and 0.6 < w / h < 1.7 and dens > 0.38):
            texts.append(c)
        elif h >= 10 and dens >= 0.12:
            graphics.append(c)

    # big digits or short bold words can look like icons. A run of same-height blobs side by side (Arabic-Indic
    # digits "١٨٪" in a bold face) is text...
    gs, runs_, done = sorted(graphics, key=lambda g: g['x0']), [], set()
    for i, g in enumerate(gs):
        if i in done:
            continue
        run = [g]
        done.add(i)
        for j in range(i + 1, len(gs)):
            if j in done:
                continue
            last, h = run[-1], gs[j]
            if (min(last['y1'], h['y1']) - max(last['y0'], h['y0']) >= 0.6 * min(last['h'], h['h'])
                    and abs(last['h'] - h['h']) <= 0.35 * max(last['h'], h['h'])
                    and 0 <= h['x0'] - last['x1'] <= 0.6 * max(last['h'], h['h'])):
                run.append(h)
                done.add(j)
        runs_.append(run)
    graphics = []
    for run in runs_:
        x0, y0 = min(g['x0'] for g in run), min(g['y0'] for g in run)
        x1, y1 = max(g['x1'] for g in run), max(g['y1'] for g in run)
        if len(run) >= 2 and (x1 - x0) >= 1.5 * (y1 - y0):
            texts.append({'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 'w': x1 - x0, 'h': y1 - y0,
                          'dens': float(np.mean([g['dens'] for g in run]))})
        else:
            graphics.extend(run)
    # ...and so is a "graphic" sitting on the same line as a text, right next to it and as tall
    keep = []
    for g in graphics:
        mate = next((t for t in texts if min(g['y1'], t['y1']) - max(g['y0'], t['y0']) >= 0.7 * min(g['h'], t['h'])
                     and abs(g['h'] - t['h']) <= 0.35 * max(g['h'], t['h'])
                     and max(g['x0'], t['x0']) - min(g['x1'], t['x1']) <= 0.8 * max(g['h'], t['h'])), None)
        (texts if mate else keep).append(g)
    graphics = keep
    for b in bars:
        mate = next((t for t in texts if t['y0'] - 2 <= b['y0'] and b['y1'] <= t['y1'] + 2 and b['h'] <= 0.35 * t['h']
                     and max(b['x0'], t['x0']) - min(b['x1'], t['x1']) <= 0.6 * t['h']), None)
        if mate:
            b['bar'] = True
            texts.append(b)

    def drop_outlines(lst):
        # a "line" that encloses two or more other lines is the outline of a shape (or the gaps between shapes),
        # not text -- unless what it encloses are its own dots and vowel marks (Arabic, Persian): small pieces
        # in a dense line
        def outline(t):
            inner = [u for u in lst if u is not t and u['x0'] >= t['x0'] and u['x1'] <= t['x1']
                     and u['y0'] >= t['y0'] and u['y1'] <= t['y1']]
            big = sum(1 for u in inner if u['h'] >= 0.2 * t['h'] and u['w'] >= 0.2 * t['h'])  # lines, not dots
            return big >= 2 or (len(inner) >= 2 and t.get('dens', 1) < 0.15)
        return [t for t in lst if not outline(t)]

    texts = drop_outlines(merge_text(drop_outlines(texts)))
    line_core = {id(t): (t['y0'], t['y1']) for t in texts}  # vertical extent before dots and accents join
    texts, marks = absorb_fragments(texts, marks)
    texts = drop_outlines(texts)
    img16 = rgb.astype(np.int16)
    out_texts = []
    for c in sorted(texts, key=lambda c: (c['y0'], c['x0'])):
        x0, y0, x1, y1 = c['x0'], c['y0'], c['x1'], c['y1']
        sub = ink[y0:y1, x0:x1]
        cy0, cy1 = line_core.get(id(c), (y0, y1))
        m = line_metrics(ink[cy0:cy1, x0:x1], cy0)  # cap / x-height / baseline from the letters, not the dots
        d = diff[y0:y1, x0:x1]
        strong = d >= np.percentile(d[sub], 70) if sub.any() else sub
        col = np.median(img16[y0:y1, x0:x1][strong], axis=0) if strong.any() else [0, 0, 0]
        back = np.median(bgl[y0:y1, x0:x1].reshape(-1, 3), axis=0)
        hl = headline_metrics(ink[cy0:cy1, x0:x1].sum(axis=1))
        out_texts.append({'box': [x0, y0, x1, y1], 'ink_top': y0, 'cap_top': m['cap_top'], 'x_top': m['x_top'],
                          'baseline': m['baseline'], 'core': [m['core_top'], m['core_bottom']],
                          'headline': [round(cy0 + hl[0], 2), round(cy0 + hl[1], 2)] if hl else None,
                          'ink_bottom': y1, 'width': x1 - x0,
                          'color': rgb_to_hex(col), 'bg': rgb_to_hex(back),
                          'light': bool(sum(col) > sum(back))})
    for k, t in enumerate(out_texts, 1):
        t['id'] = f'T{k}'

    def simple(lst, prefix, mask):
        res = []
        for k, c in enumerate(sorted(lst, key=lambda c: (c['y0'], c['x0'])), 1):
            x0, y0, x1, y1 = c['x0'], c['y0'], c['x1'], c['y1']
            sub = mask[y0:y1, x0:x1]
            if sub.any():
                d = diff[y0:y1, x0:x1]
                strong = sub & (d >= np.percentile(d[sub], 60))
                col = np.median(img16[y0:y1, x0:x1][strong if strong.any() else sub], axis=0)
            else:
                col = [0, 0, 0]
            res.append({'id': f'{prefix}{k}', 'box': [x0, y0, x1, y1], 'color': rgb_to_hex(col)})
        return res

    rules_o, graphics_o, marks_o = simple(rules, 'L', rule_mask), simple(graphics, 'G', ink), simple(marks, 'M', ink)
    for r_ in rules_o:
        x0, y0, x1, y1 = r_['box']
        r_['orientation'] = 'h' if x1 - x0 >= y1 - y0 else 'v'
        r_['thickness'] = min(x1 - x0, y1 - y0)
    analysis = {'image': os.path.abspath(a.image), 'width': width, 'height': height, 'background': bg,
                'palette': pal, 'regions': regions, 'rules': rules_o, 'graphics': graphics_o, 'marks': marks_o,
                'texts': out_texts}
    save_json(analysis, os.path.join(a.out, 'analysis.json'))

    # annotated overview
    ann = Image.fromarray(rgb).convert('RGB')
    dr = ImageDraw.Draw(ann)
    fsz = max(11, round(width / 140))
    font = ui_font(fsz)
    for lst, colr in ((regions, (30, 90, 255)), (rules_o, (0, 170, 60)), (graphics_o, (200, 0, 200)),
                      (marks_o, (255, 140, 0)), (out_texts, (230, 20, 20))):
        for e in lst:
            x0, y0, x1, y1 = e['box']
            dr.rectangle([x0, y0, x1 - 1, y1 - 1], outline=colr, width=1)
            tx, ty = x0 + 1, max(0, y0 - fsz - 1) if lst is out_texts else y0 + 1
            tw = dr.textlength(e['id'], font=font)
            dr.rectangle([tx, ty, tx + tw + 2, ty + fsz + 1], fill=(255, 255, 255))
            dr.text((tx + 1, ty), e['id'], fill=colr, font=font)
    ann.save(os.path.join(a.out, 'annotated.png'))

    # contact sheets of text lines, enlarged for transcription
    src = Image.fromarray(rgb)
    rows, sheet_no, files = [], 1, []
    font2 = ui_font(18)

    def flush(rows, no):
        if not rows:
            return None
        wmax = max(r.width for r in rows)
        sh = Image.new('RGB', (wmax, sum(r.height for r in rows)), (255, 255, 255))
        y = 0
        for r in rows:
            sh.paste(r, (0, y))
            y += r.height
        p = os.path.join(a.out, f'lines_{no}.png')
        sh.save(p)
        return p

    used = 0
    for t in out_texts:
        x0, y0, x1, y1 = t['box']
        crop = src.crop((max(0, x0 - 4), max(0, y0 - 4), min(width, x1 + 4), min(height, y1 + 4)))
        k = max(1.0, min(4.0, 44.0 / max(1, crop.height)))
        crop = crop.resize((max(1, round(crop.width * k)), max(1, round(crop.height * k))), Image.LANCZOS)
        lbl = f"{t['id']}  x={x0} base={t['baseline']}"
        row = Image.new('RGB', (crop.width + 230, crop.height + 8), (255, 255, 255))
        ImageDraw.Draw(row).text((4, 4), lbl, fill=(200, 0, 0), font=font2)
        row.paste(crop, (226, 4))
        if row.width > 2400:
            row = row.resize((2400, round(row.height * 2400 / row.width)), Image.LANCZOS)
        if used + row.height > 1800:
            files.append(flush(rows, sheet_no))
            rows, used, sheet_no = [], 0, sheet_no + 1
        rows.append(row)
        used += row.height
    files.append(flush(rows, sheet_no))

    print(f'{a.image}: {width}x{height}, background {bg}')
    print('palette:', ', '.join(f"{p['hex']} {p['coverage']}%" for p in pal[:12]))
    print(f'{len(regions)} regions R, {len(rules_o)} rules L, {len(graphics_o)} graphics G, {len(marks_o)} marks M, '
          f'{len(out_texts)} text lines T')
    print('files:', os.path.join(a.out, 'analysis.json'), os.path.join(a.out, 'annotated.png'),
          ', '.join(f for f in files if f))


if __name__ == '__main__':
    main()
