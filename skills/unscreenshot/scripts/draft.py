"""Write the whole spec of a slide from its analysis and its texts: shapes, chevrons, borders, radii, bullets,
text blocks, alignment, roles, groups, fonts, letter-spacing and paint order are decided here, by measurement,
so the result does not depend on the model that runs the skill. The model only reads the text.

    python scripts/draft.py work/analysis.json work/texts.txt --out work/spec.json

texts.txt has one line per reading line, `T7: the text exactly as read` (see run.py); an empty text means "not
text" (the line is then kept as part of the picture). Lines starting with # are comments.
Reading lines are the analysis lines with their pieces joined (reading_lines): run.py shows those to the model.
"""
import argparse
import os
import re
import sys
from collections import Counter

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import find_font_file, load_json, save_json  # noqa: E402
from textshape import guess_lang, paragraph_rtl, profile  # noqa: E402

LANG_OF = {'arabic': 'ar-SA', 'hebrew': 'he-IL', 'cjk': 'ja-JP', 'indic': 'hi-IN', 'sea': 'th-TH'}


def rel(path, start):
    """`path` relative to `start`, or absolute when they are on different drives (Windows)."""
    try:
        return os.path.relpath(path, start)
    except ValueError:
        return os.path.abspath(path)


def rgb_of(hexcol):
    h = (hexcol or '#000000').lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)])


def cdist(a, b):
    return int(np.abs(rgb_of(a) - rgb_of(b)).max())


def to_hex(c):
    return '#%02X%02X%02X' % tuple(int(round(v)) for v in c[:3])


def cap_of(t):
    return max(1.0, t['baseline'] - t.get('cap_top', t['box'][1]))


# ------------------------------------------------------------------ reading lines
def reading_lines(an):
    """Analysis lines with their pieces joined: pieces on one baseline with a small gap (CJK punctuation, wide
    digits, a second colour in the same line), and marks glued to a line (a percent sign drawn apart).
    Returns [{'id': first piece id, 'parts': [ids], 'box', 'baseline', 'cap_top', 'x_top', 'color', 'bg',
    'colors': [(x0, x1, colour)], ...}] in reading order (top to bottom, then left to right)."""
    texts = sorted(an['texts'], key=lambda t: (t['baseline'], t['box'][0]))
    marks = list(an.get('marks', []))
    graphics = list(an.get('graphics', []))
    lines = []
    texts = sorted(texts, key=lambda t: -cap_of(t))  # whole lines first, small pieces (punctuation) after
    for t in texts:
        cap = cap_of(t)
        host = None
        for ln in lines:
            lc = cap_of(ln)
            c = max(cap, lc)
            gap = max(t['box'][0] - ln['box'][2], ln['box'][0] - t['box'][2])
            if cap < 0.6 * lc:  # a small piece (CJK punctuation such as 、) inside the line's body band
                inside = t['box'][1] >= ln['baseline'] - 1.3 * lc and t['box'][3] <= ln['baseline'] + 0.4 * lc
                if inside and gap <= 1.6 * lc:
                    host = ln
                    break
                continue
            if abs(ln['baseline'] - t['baseline']) > max(2, 0.15 * c) or not 0.6 < cap / lc < 1.65:
                continue
            if gap <= 1.6 * c or (gap <= 3.2 * c and _separator_between(ln, t, marks + graphics, c)):
                host = ln
                break
        if host is None:
            ln = dict(t, parts=[t['id']], colors=[(t['box'][0], t['box'][2], t.get('color'))])
            lines.append(ln)
        else:
            host['parts'].append(t['id'])
            host['colors'].append((t['box'][0], t['box'][2], t.get('color')))
            _grow(host, t)
    used = set()
    small = marks + graphics
    # dots in a column, one per line, are bullets: never part of a line's text
    column = {m['id'] for m in marks for o in marks if o is not m and abs(o['box'][0] - m['box'][0]) <= 2
              and abs(o['box'][1] - m['box'][1]) > 2.5 * (m['box'][3] - m['box'][1]) + 8}
    for ln in lines:  # marks and thin graphics glued to a line (inside its body band, close to its ink)
        cap = cap_of(ln)
        for m in small:
            if m['id'] in used or m['id'] in column:
                continue
            x0, y0, x1, y1 = m['box']
            if y1 < ln['baseline'] - 1.3 * cap or y0 > ln['baseline'] + 0.4 * cap:
                continue
            gap = max(x0 - ln['box'][2], ln['box'][0] - x1)
            inside = ln['box'][0] < x0 and x1 < ln['box'][2]
            cy = (y0 + y1) / 2
            # a colon (two dots stacked) or a period / comma (a dot on the baseline) after a full-width glyph sits
            # far from the ink before it; a bullet dot is centred on the x-height, before the text
            stacked = any(o is not m and abs(o['box'][0] - x0) <= 2 and abs((o['box'][1] + o['box'][3]) / 2 - cy) > 0.25 * cap
                          and ln['baseline'] - 1.3 * cap <= o['box'][1] for o in small)
            on_base = cy >= ln['baseline'] - 0.25 * cap
            after = x0 >= ln['box'][2]
            if inside or gap <= 0.45 * cap or ((stacked or on_base) and after and gap <= 1.2 * cap):
                ln['parts'].append(m['id'])
                ln['colors'].append((x0, x1, m.get('color')))
                _grow(ln, {'box': m['box']})
                used.add(m['id'])
    for ln in lines:
        ln['colors'].sort()
        ln['ref'] = '+'.join(ln['parts'])
    lines.sort(key=lambda ln: (ln['baseline'], ln['box'][0]))
    return lines, used


def _separator_between(a, b, small, cap):
    """A small glyph (a "|" or a dot, drawn apart) in the gap between two pieces of one line."""
    gx0, gx1 = sorted([a['box'][2], b['box'][0]]) if a['box'][2] <= b['box'][0] else sorted([b['box'][2], a['box'][0]])
    base = a['baseline']
    for s in small:
        x0, y0, x1, y1 = s['box']
        if gx0 <= x0 and x1 <= gx1 and y1 >= base - 1.4 * cap and y0 <= base + 0.4 * cap and (x1 - x0) <= cap:
            return True
    return False


def _grow(ln, piece):
    b, p = ln['box'], piece['box']
    ln['box'] = [min(b[0], p[0]), min(b[1], p[1]), max(b[2], p[2]), max(b[3], p[3])]


# ------------------------------------------------------------------ texts file
def parse_texts(path):
    """{line id: text}, [problems]. Accepts `T7: text`, `T7 | text`, `T7 text`; # starts a comment line."""
    out, problems = {}, []
    with open(path, encoding='utf-8-sig') as f:
        for n, raw in enumerate(f, 1):
            line = raw.rstrip('\r\n')
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            m = re.match(r'\s*\[?([TtMmGg]\d+)\]?\s*(?:[:|=\-–]\s?|\s)(.*)$', line) or \
                re.match(r'\s*\[?([TtMmGg]\d+)\]?\s*$', line)
            if not m:
                problems.append(f'line {n}: no id at the start ("T7: text"): {line[:60]}')
                continue
            key = m.group(1).upper()
            text = (m.group(2) if m.lastindex and m.lastindex >= 2 else '').strip()
            if len(text) >= 2 and text[0] == text[-1] and text[0] in '"“”\'':
                text = text[1:-1]  # quotes added around the whole text
            out[key] = text
    return out, problems


# ------------------------------------------------------------------ shapes
def color_mask(rgb, col, tol=28):
    return np.abs(rgb.astype(int) - rgb_of(col)).max(axis=2) <= tol


def row_extent(mask_row, cx):
    """The run of True around column cx: (left, right) or None."""
    if cx < 0 or cx >= len(mask_row) or not mask_row[cx]:
        idx = np.nonzero(mask_row)[0]
        if not len(idx):
            return None
        cx = idx[np.argmin(np.abs(idx - cx))]
    left = cx
    while left > 0 and mask_row[left - 1]:
        left -= 1
    right = cx
    while right < len(mask_row) - 1 and mask_row[right + 1]:
        right += 1
    return left, right + 1


def chevron(rgb, reg):
    """An arrow bar (roadmap chevron): its true box, tip depth, notch and direction, or None."""
    x0, y0, x1, y1 = reg['box']
    h = y1 - y0
    if h < 12 or (x1 - x0) < 1.2 * h:
        return None
    H, W = rgb.shape[:2]
    X0, X1 = max(0, x0 - h), min(W, x1 + h)
    m = color_mask(rgb[y0:y1, X0:X1], reg['color'])
    # outermost pixels of the colour in each row: a label inside the bar must not cut the profile
    ext = []
    for r in range(h):
        idx = np.nonzero(m[r])[0]
        ext.append((idx.min(), idx.max() + 1) if len(idx) else None)
    if any(e is None for e in ext):
        return None
    L = np.array([e[0] for e in ext], float) + X0
    R = np.array([e[1] for e in ext], float) + X0
    k = max(1, h // 10)
    top, mid, bot = slice(k, 2 * k), slice(h // 2 - k, h // 2 + k), slice(h - 2 * k, h - k)
    tip_r = R[mid].mean() - (R[top].mean() + R[bot].mean()) / 2
    tip_l = (L[top].mean() + L[bot].mean()) / 2 - L[mid].mean()
    if max(tip_r, tip_l) < 0.18 * h:
        return None
    # the tip side must be straight (a rounded end bends only near the corners)
    side = R if tip_r >= tip_l else -L
    half = side[:h // 2]
    if len(half) > 6 and np.corrcoef(np.arange(len(half)), half)[0, 1] < 0.97:
        return None
    flip = tip_l > tip_r
    if not flip:
        tip = R.max() - (R[top].mean() + R[bot].mean()) / 2 + k
        notch = L[mid].mean() - (L[top].mean() + L[bot].mean()) / 2 > 2
    else:
        tip = (L[top].mean() + L[bot].mean()) / 2 - L.min() + k
        notch = (R[top].mean() + R[bot].mean()) / 2 - R[mid].mean() > 2
    el = {'type': 'arrow', 'box': [int(L.min()), y0, int(R.max()), y1], 'tip': round(float(tip), 1), 'fill': reg['color']}
    if notch:
        el['notch'] = True
    if flip:
        el['flip'] = 'h'
    return el


def border(rgb, box, fill, outside):
    """A thin outline around a filled box: (colour, width) when at least three sides show one, else None."""
    x0, y0, x1, y1 = box
    H, W = rgb.shape[:2]
    cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
    probes = [rgb[cy, max(0, x0 - 8):x0 + 4][::-1], rgb[cy, x1 - 4:min(W, x1 + 8)],
              rgb[max(0, y0 - 8):y0 + 4, cx][::-1], rgb[y1 - 4:min(H, y1 + 8), cx]]
    found = []
    for p in probes:
        run, col = 0, None
        for px in p[4:] if len(p) > 4 else []:
            c = to_hex(px)
            if cdist(c, fill) > 12 and cdist(c, outside) > 6:
                run += 1
                col = col or c
            elif run:
                break
        if 1 <= run <= 6:
            found.append((col, run))
    if len(found) < 3:
        return None
    cols = Counter(c for c, _ in found).most_common(1)[0][0]
    width = int(np.median([w for _, w in found]))
    return cols, width


def corner_radius(rgb, box, col, others=()):
    """Radius of the rounded corners of a box, fitted on the four corner profiles (0 for square corners).
    A pixel belongs to the shape when it is closer to `col` than to the `others` (the colours around it): a white
    card on a near-white page differs from it by a few levels only."""
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    if w < 8 or h < 8:
        return 0.0
    sub = rgb[y0:y1, x0:x1].astype(int)
    d = np.abs(sub - rgb_of(col)).max(axis=2)
    m = d <= 30
    for o in others:
        m &= d < np.abs(sub - rgb_of(o)).max(axis=2)
    n = min(h // 2, w // 2, 80)
    insets = []
    for rows, flipx in ((m[:n], False), (m[:n], True), (m[::-1][:n], False), (m[::-1][:n], True)):
        prof = []
        for r in rows:
            r = r[::-1] if flipx else r
            idx = np.nonzero(r)[0]
            prof.append(idx[0] if len(idx) else w)
        insets.append(np.array(prof, float))
    inset = np.median(np.stack(insets), axis=0)
    best, err = 0.0, float(np.mean(inset ** 2))
    for r in np.arange(1, n + 0.5, 0.5):
        i = np.arange(n)
        model = np.where(i < r, r - np.sqrt(np.maximum(0, r * r - (r - i - 0.5) ** 2)), 0)
        e = float(np.mean((inset - model) ** 2))
        if e < err:
            best, err = r, e
    return round(best, 1)


def shapes(rgb, an):
    W, H = an['width'], an['height']
    bg = an['background']
    out = []
    for reg in sorted(an['regions'], key=lambda r: -(r['box'][2] - r['box'][0]) * (r['box'][3] - r['box'][1])):
        x0, y0, x1, y1 = reg['box']
        if (x1 - x0) * (y1 - y0) > 0.9 * W * H:
            continue  # the slide background
        if reg.get('kind') == 'container' and cdist(reg['color'], bg) <= 6:
            continue  # a frame of the background colour: nothing to draw
        host = container_of(reg['box'], out)
        if host is not None and host['type'] != 'arrow' and cdist(host.get('fill'), reg['color']) <= 6:
            continue  # a patch of a shape's own colour inside it (between texts): already drawn
        el = chevron(rgb, reg) if reg.get('shape') in ('roundrect', 'pill', 'rect') else None
        if el is None:
            if reg.get('shape') == 'ellipse':
                el = {'type': 'ellipse', 'box': list(reg['box']), 'fill': reg['color']}
            else:
                el = {'type': 'rect', 'box': list(reg['box']), 'fill': reg['color']}
                outside = _outside_colour(rgb, reg['box'], bg)
                b = border(rgb, reg['box'], reg['color'], outside)
                if b:
                    col, width = b
                    el['line'] = {'color': col, 'width': width}
                    el['box'] = [x0 - width, y0 - width, x1 + width, y1 + width]
                    r = corner_radius(rgb, el['box'], b[0], (reg['color'], outside))
                else:
                    r = corner_radius(rgb, el['box'], reg['color'], (outside,))
                thin = min(y1 - y0, x1 - x0) < 16  # a bar: its corner profile says nothing
                if reg.get('shape') == 'pill' or (not thin and r >= 0.45 * min(y1 - y0, x1 - x0)):
                    el['radius'] = 'pill'
                elif r >= 2 and not thin:
                    el['radius'] = r
        el['src'] = reg['id']
        out.append(el)
    _share_radii(out)
    return out


def _outside_colour(rgb, box, bg):
    x0, y0, x1, y1 = box
    H, W = rgb.shape[:2]
    samples = [rgb[max(0, y0 - 10), (x0 + x1) // 2], rgb[min(H - 1, y1 + 10), (x0 + x1) // 2],
               rgb[(y0 + y1) // 2, max(0, x0 - 10)], rgb[(y0 + y1) // 2, min(W - 1, x1 + 10)]]
    return to_hex(np.median(np.array(samples), axis=0))


def _share_radii(els):
    """Cards of one size and colour get one radius (the median of what was measured on each)."""
    rects = [e for e in els if e['type'] == 'rect' and isinstance(e.get('radius', 0), (int, float))]
    for e in rects:
        w, h = e['box'][2] - e['box'][0], e['box'][3] - e['box'][1]
        sib = [s for s in rects if abs((s['box'][2] - s['box'][0]) - w) <= 4 and abs((s['box'][3] - s['box'][1]) - h) <= 4
               and s['fill'] == e['fill']]
        if len(sib) >= 2:
            r = float(np.median([s.get('radius', 0) for s in sib]))
            for s in sib:
                if r >= 2:
                    s['radius'] = round(r, 1)
                else:
                    s.pop('radius', None)


# ------------------------------------------------------------------ text structure
def container_of(box, shapes_):
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    inside = [s for s in shapes_ if s['box'][0] <= cx <= s['box'][2] and s['box'][1] <= cy <= s['box'][3]]
    return min(inside, key=lambda s: (s['box'][2] - s['box'][0]) * (s['box'][3] - s['box'][1])) if inside else None


def is_rtl_text(text, lang):
    return paragraph_rtl(text, None, lang)


def bullets_of(lines, marks, texts, slide_lang):
    """Bullet lists: a dot beside a line (left of it, or right of it in right-to-left text)."""
    items = []
    for m in marks:
        mx0, my0, mx1, my1 = m['box']
        mcy = (my0 + my1) / 2
        best = None
        for ln in lines:
            if ln.get('used'):
                continue
            cap = cap_of(ln)
            if not (ln['baseline'] - 1.1 * cap <= mcy <= ln['baseline'] + 0.1 * cap):
                continue
            rtl = is_rtl_text(texts.get(ln['id'], ''), slide_lang)
            gap = (mx0 - ln['box'][2]) if rtl else (ln['box'][0] - mx1)
            if 0.2 * cap <= gap <= 4 * cap and (best is None or gap < best[0]):
                best = (gap, ln, rtl)
        if best:
            items.append({'mark': m, 'line': best[1], 'rtl': best[2]})
    lists = []
    for it in sorted(items, key=lambda i: i['line']['baseline']):
        key = round((it['mark']['box'][2] if it['rtl'] else it['mark']['box'][0]) / 4)
        for lst in lists:
            if abs(lst['key'] - key) <= 1 and lst['rtl'] == it['rtl']:
                lst['items'].append(it)
                break
        else:
            lists.append({'key': key, 'rtl': it['rtl'], 'items': [it]})
    for lst in lists:
        for it in lst['items']:
            it['line']['used'] = True
            it['lines'] = [it['line']]
    # continuation lines: below an item, aligned with its text, before the next item
    for lst in lists:
        its = lst['items']
        for k, it in enumerate(its):
            nxt = its[k + 1]['line']['baseline'] if k + 1 < len(its) else None
            last = it['line']
            for ln in sorted(lines, key=lambda l_: l_['baseline']):
                if ln.get('used') or ln['baseline'] <= last['baseline'] or (nxt and ln['baseline'] >= nxt):
                    continue
                cap = cap_of(last)
                edge_ok = abs((ln['box'][2] - last['box'][2]) if lst['rtl'] else (ln['box'][0] - it['line']['box'][0])) <= 0.6 * cap
                if edge_ok and ln['baseline'] - last['baseline'] <= 2.4 * cap and cdist(ln['color'], last['color']) <= 40:
                    ln['used'] = True
                    it['lines'].append(ln)
                    last = ln
    return lists


def blocks_of(lines, shapes_):
    """Multi-line text blocks: same colour and size, aligned, at a regular line pitch, in the same container."""
    free = sorted([ln for ln in lines if not ln.get('used')], key=lambda l_: (l_['baseline'], l_['box'][0]))
    blocks = []
    for ln in free:
        cap = cap_of(ln)
        host = None
        for b in blocks:
            last = b['lines'][-1]
            lc = cap_of(last)
            if b['container'] is not container_of(ln['box'], shapes_) or cdist(ln['color'], last['color']) > 30:
                continue
            if not 0.8 < cap / lc < 1.25:
                continue
            gap = ln['baseline'] - last['baseline']
            if not 1.25 * lc <= gap <= 2.7 * lc:
                continue
            if len(b['lines']) >= 2:
                pitch = b['lines'][-1]['baseline'] - b['lines'][-2]['baseline']
                if abs(gap - pitch) > 0.15 * pitch:
                    continue
            tol = 0.6 * max(cap, lc)
            aligned = [abs(ln['box'][0] - last['box'][0]) <= tol, abs(ln['box'][2] - last['box'][2]) <= tol,
                       abs((ln['box'][0] + ln['box'][2]) / 2 - (last['box'][0] + last['box'][2]) / 2) <= tol]
            if any(aligned):
                host = b
                break
        if host:
            host['lines'].append(ln)
        else:
            blocks.append({'lines': [ln], 'container': container_of(ln['box'], shapes_)})
    return blocks


def alignment(lines, container, rtl):
    if len(lines) > 1:
        cap = cap_of(lines[0])
        tol = 0.6 * cap
        x0s, x1s = [l_['box'][0] for l_ in lines], [l_['box'][2] for l_ in lines]
        cs = [(a + b) / 2 for a, b in zip(x0s, x1s)]
        left, right = max(x0s) - min(x0s) <= tol, max(x1s) - min(x1s) <= tol
        center = max(cs) - min(cs) <= tol
        if left and right:
            return 'right' if rtl else 'left'
        if left:
            return 'left'
        if right:
            return 'right'
        if center:
            return 'center'
        return 'right' if rtl else 'left'
    ln = lines[0]
    if container is not None and container['type'] in ('rect', 'ellipse', 'arrow'):
        cx0, _, cx1, _ = container['box']
        cw = cx1 - cx0
        lc = (ln['box'][0] + ln['box'][2]) / 2
        pad_l, pad_r = ln['box'][0] - cx0, cx1 - ln['box'][2]
        if abs(lc - (cx0 + cx1) / 2) <= 0.04 * cw and min(pad_l, pad_r) > 0.08 * cw:
            return 'center'
    return 'right' if rtl else 'left'


def runs_for(text, ln):
    """Split a line read as one text into coloured runs when its pieces have different colours."""
    cols = [c for c in ln['colors'] if c[2]]
    if len({c[2] for c in cols}) < 2 or not text:
        return None
    x0, x1 = ln['box'][0], ln['box'][2]
    # character positions spread over the ink width (proportional estimate), each character takes the colour of the
    # piece under it; spaces join the run before them
    n = len(text)
    out = []
    for i, ch in enumerate(text):
        x = x0 + (i + 0.5) / n * (x1 - x0)
        col = min(cols, key=lambda c: 0 if c[0] <= x <= c[1] else min(abs(x - c[0]), abs(x - c[1])))[2]
        if ch.isspace() and out:
            col = out[-1][1]
        if out and out[-1][1] == col:
            out[-1][0] += ch
        else:
            out.append([ch, col])
    merged = []
    for t, c in out:
        if merged and cdist(merged[-1]['color'], c) <= 30:
            merged[-1]['text'] += t
        else:
            merged.append({'text': t, 'color': c})
    return merged if len(merged) > 1 else None


# ------------------------------------------------------------------ assembly
def draft(an, texts, source_png, spec_dir):
    rgb = np.asarray(Image.open(source_png).convert('RGB'))
    lines, glued = reading_lines(an)
    all_text = ' '.join(texts.get(ln['id'], '') for ln in lines)
    fams = Counter()
    for ln in lines:
        t = texts.get(ln['id'], '')
        if t:
            fams[profile(t)['family']] += len(t)
    main_family = fams.most_common(1)[0][0] if fams else 'alphabetic'
    slide_lang = LANG_OF.get(main_family) or guess_lang(all_text, 'en-US')
    if main_family == 'cjk':
        slide_lang = guess_lang(all_text, 'ja-JP' if re.search('[぀-ヿ]', all_text) else 'zh-CN')
    if main_family == 'arabic' and re.search('[پچگکی]', all_text):
        slide_lang = 'fa-IR'
    lines = [ln for ln in lines if texts.get(ln['id'], '').strip()]
    shapes_ = shapes(rgb, an)
    marks = [m for m in an.get('marks', []) if m['id'] not in glued]
    lists = bullets_of(lines, marks, texts, slide_lang)
    blocks = blocks_of(lines, shapes_)
    els = []
    # shapes: largest first, then rules, pictures and loose dots
    for k, s in enumerate(shapes_, 1):
        e = {'id': f"{s['type']}{k}" if s['type'] != 'arrow' else f'arrow{k}', **{a: b for a, b in s.items() if a != 'src'}}
        e['from'] = s['src']
        if e['type'] == 'arrow' or 'line' in e:
            e.pop('from')
        els.append(e)
    for r in an.get('rules', []):
        els.append({'id': f"rule-{r['id']}", 'type': 'line', 'from': r['id'], 'color': r['color']})
    for g in an.get('graphics', []):
        if g['id'] not in glued:
            els.append({'id': f"picture-{g['id']}", 'type': 'image', 'box': g['box'], 'transparent': 'auto', 'upscale': 4})
    bullet_marks = {it['mark']['id'] for lst in lists for it in lst['items']}
    for m in marks:
        if m['id'] not in bullet_marks:
            els.append({'id': f"dot-{m['id']}", 'type': 'ellipse', 'box': m['box'], 'fill': m['color']})
    # texts
    text_els = []
    for b in blocks:
        ls = b['lines']
        txt = [texts[ln['id']] for ln in ls]
        lang = guess_lang(' '.join(txt), slide_lang)
        rtl = is_rtl_text(' '.join(txt), lang)
        e = {'type': 'text', 'from': [ln['ref'] for ln in ls], 'lines': [], 'align': alignment(ls, b['container'], rtl)}
        for ln, t in zip(ls, txt):
            e['lines'].append(runs_for(t, ln) or t)
        if lang != slide_lang:
            e['lang'] = lang
        e['_lines'], e['_container'] = ls, b['container']
        text_els.append(e)
    for lst in lists:
        its = lst['items']
        first = its[0]
        txt = [[texts[ln['id']] for ln in it['lines']] for it in its]
        lang = guess_lang(' '.join(t for item in txt for t in item), slide_lang)
        m = first['mark']
        dot_h = m['box'][3] - m['box'][1]
        cap = cap_of(first['line'])
        e = {'type': 'bullets', 'from': [ln['ref'] for it in its for ln in it['lines']],
             'items': [t[0] if len(t) == 1 else t for t in txt],
             'x': m['box'][2] if lst['rtl'] else m['box'][0], 'bullet': '●', 'bullet_color': m['color'],
             'bullet_size': int(max(60, min(160, round(100 * dot_h / (0.42 * cap / 0.7)))))}
        if lang != slide_lang:
            e['lang'] = lang
        e['_lines'] = [ln for it in its for ln in it['lines']]
        e['_container'] = container_of(first['line']['box'], shapes_)
        text_els.append(e)
    _fonts(rgb, text_els, slide_lang)
    _roles(text_els)
    _spacing(rgb, text_els)
    _groups(els, text_els)
    text_els.sort(key=lambda e: (e['_lines'][0]['baseline'], e['_lines'][0]['box'][0]))
    for k, e in enumerate(text_els, 1):
        e['id'] = f'text{k}' if e['type'] == 'text' else f'list{k}'
        for key in ('_lines', '_container'):
            e.pop(key, None)
        els.append(e)
    title = next((e['lines'][0] if isinstance(e['lines'][0], str) else ''.join(r['text'] for r in e['lines'][0])
                  for e in els if e['type'] == 'text'), 'Slide')
    return {'source': rel(source_png, spec_dir), 'analysis': 'analysis.json', 'size': [an['width'], an['height']],
            'background': an['background'], 'lang': slide_lang, 'title': title[:80], 'elements': els}


def _fonts(rgb, text_els, slide_lang):
    import fontmatch
    groups = []
    for e in text_els:
        ls = e['_lines']
        src = e['lines'] if e['type'] == 'text' else [t for it in e['items'] for t in (it if isinstance(it, list) else [it])]
        flat = [s if isinstance(s, str) else ''.join(r['text'] for r in s) for s in src]
        groups.append(list(zip(ls, flat)))
    picks = fontmatch.match(rgb, groups, slide_lang)
    for e, p in zip(text_els, picks):
        if p:
            e['font'] = p[0]
            if p[1]:
                e['bold'] = True


def _roles(text_els):
    """Texts of one kind (three KPI figures, four chevron labels...) share a size: same font, colour, size and
    number of lines, two or more of them."""
    def key(e):
        ln = e['_lines'][0]
        return (e['type'], e.get('font'), bool(e.get('bold')), len(e['_lines']))
    pool = [e for e in text_els if e['type'] == 'text']
    k = 0
    for e in pool:
        if e.get('role'):
            continue
        cap = cap_of(e['_lines'][0])
        sib = [s for s in pool if not s.get('role') and key(s) == key(e)
               and 0.88 < cap_of(s['_lines'][0]) / cap < 1.14 and cdist(s['_lines'][0]['color'], e['_lines'][0]['color']) <= 30]
        if len(sib) >= 2:
            k += 1
            for s in sib:
                s['role'] = f'role{k}'


def _spacing(rgb, text_els):
    """Letter-spaced capitals: the measured width is well above the font's natural width at the measured cap
    height. They are fitted on the cap height, with letter-spacing from the width."""
    import fontmatch
    for e in text_els:
        if e['type'] != 'text' or len(e['_lines']) != 1:
            continue
        text = e['lines'][0] if isinstance(e['lines'][0], str) else ''.join(r['text'] for r in e['lines'][0])
        if not fontmatch.is_caps(text) or profile(text)['joined']:
            continue
        path = find_font_file(e.get('font', 'Arial'), bold=bool(e.get('bold')))[0]
        if not path:
            continue
        ln = e['_lines'][0]
        c = fontmatch.candidate_features(path, text, cap_of(ln), 'alphabetic')
        if c and (ln['box'][2] - ln['box'][0]) / c['w'] > 1.12:
            e['fit'] = {'mode': 'spacing'}


def _groups(shape_els, text_els):
    """A card and what sits on it form a group; a row of chevrons and their labels too."""
    by_src = {}
    for e in shape_els:
        if e['type'] in ('rect', 'ellipse', 'arrow'):
            by_src[tuple(e['box'])] = e
    n = 0
    for e in text_els:
        c = e.get('_container')
        if c is None:
            continue
        host = by_src.get(tuple(c['box'])) or next((s for s in shape_els if s.get('from') == c.get('src')), None)
        if host is None:
            continue
        if 'group' not in host:
            n += 1
            host['group'] = f'group{n}'
        e['group'] = host['group']
    arrows = [s for s in shape_els if s['type'] == 'arrow']
    rows = {}
    for a in arrows:
        rows.setdefault((round(a['box'][1] / 6), round(a['box'][3] / 6)), []).append(a)
    for row in rows.values():
        if len(row) >= 2:
            n += 1
            name = f'group{n}'
            old = {a.get('group') for a in row}
            for a in row:
                a['group'] = name
            for e in text_els:
                if e.get('group') in old and e.get('group'):
                    e['group'] = name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('analysis')
    ap.add_argument('texts')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    an = load_json(a.analysis)
    texts, problems = parse_texts(a.texts)
    for p in problems:
        print('  !', p)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.analysis)), 'spec.json')
    spec = draft(an, texts, an['image'], os.path.dirname(os.path.abspath(out)))
    spec['analysis'] = rel(os.path.abspath(a.analysis), os.path.dirname(os.path.abspath(out)))
    save_json(spec, out)
    kinds = Counter(e['type'] for e in spec['elements'])
    print(f"spec: {len(spec['elements'])} elements ({', '.join(f'{v} {k}' for k, v in kinds.items())}), "
          f"lang {spec['lang']} -> {out}")


if __name__ == '__main__':
    main()
