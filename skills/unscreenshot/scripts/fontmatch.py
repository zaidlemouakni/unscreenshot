"""Pick the Office font and weight that look closest to the text of a slide image, by measurement.

For each line, the image gives its cap height, x-height, ink width and stroke thickness. Every installed candidate
font renders the same text at the size where its capitals match the image, and is scored on the ink width, the
x-height / cap-height ratio and the stroke thickness. Lines of the same style are scored together (one font per
style), and a slide keeps three families at most. Fonts that are not installed are not candidates: on a machine
without Office fonts, the script's default font is used and the weight comes from the stroke thickness alone.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

from common import find_font_file, load_font
from textshape import EA_DEFAULT, arabic_shape, guess_lang, profile, visual

# one font per style (neutral, humanist, geometric, narrow, serif, monospace): close look-alikes only add noise
LATIN = ['Arial', 'Segoe UI', 'Segoe UI Semibold', 'Century Gothic', 'Calibri', 'Georgia', 'Times New Roman',
         'Courier New']
SCRIPT = {'arabic': ['Segoe UI', 'Segoe UI Semibold', 'Dubai'],
          'hebrew': ['Segoe UI', 'Segoe UI Semibold', 'Arial'],
          'indic': ['Nirmala UI'], 'sea': ['Leelawadee UI']}
DEFAULT = {'alphabetic': 'Arial', 'arabic': 'Segoe UI', 'hebrew': 'Segoe UI', 'indic': 'Nirmala UI',
           'sea': 'Leelawadee UI'}
# weights of one family are compared on stroke coverage, not on letter shapes
WEIGHT_FAMILY = {'segoe ui semibold': 'Segoe UI'}
# screen renderers (browsers, Office, Keynote) draw text darker than Pillow's linear coverage: measured 1.13-1.30
# on regular and bold Segoe UI and Arial lines of Chrome screenshots
RENDER_GAIN = 1.18
_cache = {}


def _rgb(hexcol):
    h = (hexcol or '#000000').lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)])


def stem_width(mask, rows=None):
    """Median length of the horizontal ink runs (the thickness of vertical strokes), in px."""
    m = mask if rows is None else mask[rows[0]:rows[1]]
    runs = []
    for row in m:
        if not row.any():
            continue
        d = np.diff(np.concatenate([[0], row.astype(np.int8), [0]]))
        starts, ends = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
        runs.extend((ends - starts).tolist())
    return float(np.median(runs)) if runs else 0.0


def source_features(rgb, line):
    """Measurements of one analysed text line (an analysis `T#` entry) on the slide image, and its ink mask."""
    x0, y0, x1, y1 = [int(v) for v in line['box']]
    sub = rgb[y0:y1 + 1, x0:x1 + 1].astype(int)
    col, bg = _rgb(line.get('color')), _rgb(line.get('bg'))
    d_col, d_bg = np.abs(sub - col).max(axis=2), np.abs(sub - bg).max(axis=2)
    ink = (d_col < d_bg) & (d_bg > 30)
    base, cap_top, x_top = line['baseline'], line.get('cap_top', y0), line.get('x_top', y0)
    cap = max(1.0, base - cap_top)
    band = (int(max(0, x_top - y0)), int(max(1, base - y0)))
    # stroke weight: the mean ink coverage (anti-aliasing included) in the x-height band
    alpha = np.clip(d_bg / max(1, np.abs(col - bg).max()), 0, 1)
    dark = float(alpha[band[0]:band[1]].mean()) if band[1] > band[0] else 0.0
    return {'w': float(x1 - x0), 'cap': cap, 'xr': (base - x_top) / cap, 'stem': stem_width(ink, band),
            'mask': _tight(ink), 'top': y0, 'base': base, 'dark': dark}



MAX_CAP = 22  # shapes are compared with capitals this tall at most: large headings render much faster


def _downscaled(f):
    """The measurements of a large line scaled so its capitals are MAX_CAP px (coverage does not change)."""
    k = MAX_CAP / f['cap']
    if k >= 1:
        return f
    h, w = f['mask'].shape
    m = Image.fromarray((f['mask'] * 255).astype(np.uint8)).resize((max(1, round(w * k)), max(1, round(h * k))),
                                                                   Image.BILINEAR)
    return dict(f, mask=np.asarray(m) > 110, cap=f['cap'] * k, w=f['w'] * k, stem=f['stem'] * k)


def _tight(mask):
    ys, xs = np.nonzero(mask)
    return mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1] if len(xs) else mask


def shape_similarity(src_mask, cand_mask):
    """F1 of the two ink masks (1 px tolerance) once the candidate is scaled to the source's width, aligned on the
    bottom of the ink: how much the letter shapes, weights and proportions agree."""
    h, w = src_mask.shape
    ch, cw = cand_mask.shape
    if not (h and w and ch and cw):
        return 0.0
    k = w / cw
    nh = max(1, int(round(ch * k)))
    scaled = np.asarray(Image.fromarray((cand_mask * 255).astype(np.uint8)).resize((w, nh), Image.BILINEAR)) > 110
    H = max(h, nh)
    a = np.zeros((H, w), bool)
    b = np.zeros((H, w), bool)
    a[H - h:] = src_mask
    b[H - nh:] = scaled
    from common import box_any
    if not a.any() or not b.any():
        return 0.0
    precision = (b & box_any(a, 1, 1)).sum() / b.sum()
    recall = (a & box_any(b, 1, 1)).sum() / a.sum()
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def _font_metrics(path):
    if path not in _cache:
        f = load_font(path, 200)
        h, x = _ink_box(f, 'H'), _ink_box(f, 'x')
        _cache[path] = ((h[3] - h[1]) / 200.0, (x[3] - x[1]) / max(1, h[3] - h[1]))
    return _cache[path]


def _ink_box(font, text):
    img = _render(font, text)
    ys, xs = np.nonzero(img)
    return (0, 0, 0, 0) if not len(xs) else (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)


def _render(font, text, gray=False):
    w = int(font.getlength(text)) + font.size * 2 + 8
    img = Image.new('L', (max(8, w), int(font.size * 2.2) + 8), 0)
    ImageDraw.Draw(img).text((font.size, font.size * 0.4), text, fill=255, font=font)
    a = np.asarray(img)
    return a / 255.0 if gray else a > 110


def candidate_features(path, text, cap, family):
    """The same measurements for `text` drawn with the font at `path`, sized so its capitals are `cap` px."""
    cap_ratio, xr = _font_metrics(path)
    size = max(4, cap / max(0.3, cap_ratio))
    font = load_font(path, int(round(size)))
    shown = visual(arabic_shape(text), True) if family == 'arabic' else text
    gray = _render(font, shown, gray=True)
    mask = gray > 110 / 255.0
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None
    # thickness measured in the x-height band, like on the image; both scaled to the image's cap height
    hbox = _ink_box(font, 'H')
    k = cap / max(1, hbox[3] - hbox[1])
    band = (int(hbox[3] - xr * (hbox[3] - hbox[1])), int(hbox[3]))
    dark = float(gray[band[0]:band[1], xs.min():xs.max() + 1].mean()) if band[1] > band[0] else 0.0
    return {'w': float(xs.max() + 1 - xs.min()) * k, 'xr': xr, 'stem': stem_width(mask, band) * k,
            'mask': _tight(mask), 'dark': dark}


def candidates(family, lang):
    if family == 'alphabetic':
        names = LATIN
    elif family == 'cjk':
        tag = (lang or '').lower()
        key = 'zh-hant' if tag.startswith(('zh-tw', 'zh-hk', 'zh-mo')) else tag.split('-')[0]
        names = [EA_DEFAULT.get(key, 'Microsoft YaHei')]
    else:
        names = SCRIPT.get(family, [DEFAULT.get(family, 'Arial')])
    out = []
    for name in names:
        for bold in ((False,) if 'semibold' in name.lower() else (False, True)):
            path, exact, _ = find_font_file(name, bold=bold)
            if path and exact:
                out.append((name, bold, path))
    return out


def score(src, cand, use_width, use_xr):
    e = 1.5 * abs(math.log(max(0.3, cand['stem']) / max(0.3, src['stem'])))
    if use_width:
        e += 3.0 * abs(math.log(cand['w'] / max(1.0, src['w'])))
    if use_xr:
        e += 2.0 * abs(cand['xr'] - src['xr'])
    return e


def is_caps(text):
    letters = [c for c in text if c.isalpha()]
    return len(letters) >= 3 and sum(c.isupper() for c in letters) >= 0.8 * len(letters)


def match(rgb, groups, lang='en-US'):
    """groups: [[(analysis line, text), ...], ...], one list per style. Returns [(font, bold, exact?)] in order."""
    results, caps_groups, families = [], [], []
    for g, lines in enumerate(groups):
        lines = [(ln, t) for ln, t in lines if t and t.strip()]
        if not lines:
            results.append(None)
            families.append(None)
            continue
        joined = ' '.join(t for _, t in lines)
        fam = profile(joined)['family']
        lines = sorted(lines, key=lambda lt: -(lt[0]['box'][2] - lt[0]['box'][0]))[:2]  # the two longest
        feats = [(_downscaled(source_features(rgb, ln)), t) for ln, t in lines]
        # weak evidence on the family: spaced capitals, or too few letters (a page number, a KPI figure)
        caps = fam == 'alphabetic' and (all(is_caps(t) for _, t in feats) or sum(c.isalpha() for c in joined) < 6)
        cands = candidates(fam, guess_lang(joined, lang))
        families.append(fam)
        if not cands:  # nothing installed: the script's font, the weight from the stroke thickness
            ratio = np.median([f['stem'] / f['cap'] for f, _ in feats])
            results.append((DEFAULT.get(fam, 'Arial'), bool(ratio > 0.17), False))
            continue
        # family: the best letter-shape match over its weights; weight: the closest stroke coverage in that family
        shape, weight = {}, {}
        for name, bold, path in cands:
            sim, dev, n = 0.0, 0.0, 0
            for f, t in feats:
                c = candidate_features(path, t, f['cap'], fam)
                if c:
                    sim += shape_similarity(f['mask'], c['mask'])
                    dev += abs(math.log(max(0.02, c['dark']) / max(0.02, f['dark'] / RENDER_GAIN)))
                    n += 1
            if n:
                base = WEIGHT_FAMILY.get(name.lower(), name)
                shape[base] = max(shape.get(base, 0.0), sim / n)
                weight[(name, bold)] = (dev / n, base)
        if not shape:
            results.append((DEFAULT.get(fam, 'Arial'), False, False))
            continue
        fams = sorted(shape, key=lambda b: -shape[b])
        scored = sorted((weight[k][0] + 2.0 * (shape[fams[0]] - shape[weight[k][1]]), k[0], k[1]) for k in weight)
        best = min(((d, n, b) for (n, b), (d, base) in weight.items() if base == fams[0]), default=None)
        if best:
            scored.insert(0, best)
        results.append((scored[0][1], scored[0][2], True) if scored else (DEFAULT.get(fam, 'Arial'), False, False))
        if caps:
            caps_groups.append((g, scored))
    # spaced capitals say little about the family: take the slide's Latin family of the same weight when there is one
    caps_ids = {c[0] for c in caps_groups}
    others = [r for g, r in enumerate(results) if r and g not in caps_ids and families[g] == 'alphabetic']
    for g, scored in caps_groups:
        if not scored or not others:
            continue
        weight = results[g][1]
        names = [r[0] for r in others if r[1] == weight] or [r[0] for r in others]
        best = max(set(names), key=names.count)
        pick = next(((s, n, b) for s, n, b in scored if n == best), None)
        if pick:
            results[g] = (pick[1], pick[2], True)
    return _limit_families(results, families)


def _limit_families(results, families, keep=3):
    """Three Latin families per slide at most (other scripts keep the font that draws them)."""
    names = [r[0] for r, f in zip(results, families) if r and f == 'alphabetic']
    if len(set(names)) <= keep:
        return results
    top = sorted(set(names), key=lambda n: -names.count(n))[:keep]
    return [r if not r or f != 'alphabetic' or r[0] in top else (top[0], r[1], r[2])
            for r, f in zip(results, families)]
