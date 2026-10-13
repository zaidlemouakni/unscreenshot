"""Complete a spec from the analysis and fit the typography, for any writing system.

    python scripts/fit.py work/spec.json [--analysis work/analysis.json] [--out work/spec.fitted.json]

1. Resolves "from" references: T# (text lines), R# (regions), L# (rules), G#/M# (graphics, marks) fill in
   missing geometry and colours (x, baseline, w, cap, pitch, line boxes for texts; box, fill, radius for shapes;
   from/to/width/color for lines; box for images). Values already present in the spec are kept. Right-to-left
   texts anchor on their right edge.
2. Fits the font size so each text's ink width matches the source, with the font PowerPoint will use for that
   script (real font or metric twin). Scripts that cannot be measured in width here (Indic without a shaping
   engine...) are fitted on their ink height. "spacing" mode fits letter-spacing too (never for joined scripts).
3. For non-Latin scripts, corrects the analysis baseline (the bottom of the densest band of ink rows: the
   headline in Devanagari, the letter bodies in CJK) by where that band falls in the font itself.
"""
import argparse
import os
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (cap_ratio, find_font_file, find_lang_font, load_font, load_json, save_json,  # noqa: E402
                    split_index)
from textshape import (HEADLINE_SCRIPTS, bands, guess_lang, ink_extents, measure, measuring_font,  # noqa: E402
                       missing_glyphs, paragraph_rtl, profile)

M = 200  # measuring size (px)
# fit methods that solve the size from the font's own measured glyphs; the others ('body height', 'height',
# 'cap') estimate it
MEASURED = ('width', 'cap+spacing', 'height+spacing', 'headline')


def index_analysis(an):
    idx = {}
    for key in ('texts', 'regions', 'rules', 'graphics', 'marks'):
        for e in an.get(key, []):
            idx[e['id']] = e
    return idx


def element_lines(el):
    """Plain text of each line of a text or bullets element."""
    if el['type'] == 'bullets':
        lines = []
        for it in el.get('items', []):
            lines += it if isinstance(it, list) else [it]
    else:
        lines = el.get('lines') or [el.get('text', '')]
    return [ln if isinstance(ln, str) else ''.join(r.get('text', '') for r in ln) for ln in lines]


def is_rtl(el, slide_lang='en-US'):
    return paragraph_rtl(' '.join(element_lines(el)), el.get('dir'), el.get('lang') or slide_lang)


def join_pieces(pieces):
    """One line from several analysis pieces ("G1+G2+T5"): union box; text metrics from the widest piece that
    has them (a line made only of graphics gets no baseline: fit places it from its ink box)."""
    x0, y0 = min(p['box'][0] for p in pieces), min(p['box'][1] for p in pieces)
    x1, y1 = max(p['box'][2] for p in pieces), max(p['box'][3] for p in pieces)
    out = {'id': '+'.join(p['id'] for p in pieces), 'box': [x0, y0, x1, y1],
           'color': next((p['color'] for p in pieces if p.get('color')), None)}
    texts = [p for p in pieces if 'baseline' in p]
    if texts:
        best = max(texts, key=lambda p: p['box'][2] - p['box'][0])
        for k in ('baseline', 'cap_top', 'x_top', 'core', 'headline', 'color'):
            if best.get(k) is not None:
                out[k] = best[k]
    return out


def resolve(el, idx, slide_lang='en-US'):
    ref = el.get('from')
    if not ref:
        return
    refs = ref if isinstance(ref, list) else [ref]
    ents, missing = [], []
    for r in refs:  # each entry is one line; "G1+G2" joins pieces of the same line
        parts = [p.strip() for p in str(r).split('+')]
        missing += [p for p in parts if p not in idx]
        found = [idx[p] for p in parts if p in idx]
        if found:
            ents.append(found[0] if len(found) == 1 else join_pieces(found))
    if missing:
        print(f"  ! {el.get('id')}: unknown references {missing}")
    if not ents:
        return
    t = el['type']
    if t in ('text', 'bullets'):
        first = ents[0]
        if 'baseline' not in el and 'baseline' in first:
            el['baseline'] = first['baseline']
            el['baseline_from'] = 'analysis'
        el.setdefault('color', first.get('color'))
        if 'cap_top' in first:
            el.setdefault('cap', first['baseline'] - first['cap_top'])
            el.setdefault('xh', first['baseline'] - first['x_top'])
        el.setdefault('line_boxes', [e['box'] for e in ents])
        if all('core' in e for e in ents):
            el.setdefault('line_core', [e['core'] for e in ents])
        if all(e.get('headline') for e in ents):
            el.setdefault('line_headline', [e['headline'] for e in ents])
        if len(ents) > 1 and 'pitch' not in el and all('baseline' in e for e in ents):
            bs = sorted(e['baseline'] for e in ents)
            el['pitch'] = round((bs[-1] - bs[0]) / (len(bs) - 1), 2)
        el.setdefault('line_w', [e['box'][2] - e['box'][0] for e in ents])
        rtl = is_rtl(el, slide_lang)
        x0 = min(e['box'][0] for e in ents)
        x1 = max(e['box'][2] for e in ents)
        if t == 'text':
            align = el.setdefault('align', 'right' if rtl else 'left')
            el.setdefault('x', x0 if align == 'left' else x1 if align == 'right' else (x0 + x1) / 2)
        else:
            el.setdefault('text_x', x1 if rtl else x0)
        el.setdefault('w', max(e['box'][2] - e['box'][0] for e in ents))
    elif t in ('rect', 'ellipse', 'arrow'):
        e = ents[0]
        el.setdefault('box', e['box'])
        el.setdefault('fill', e.get('color'))
        if t == 'rect' and 'radius' not in el:
            if e.get('shape') == 'pill':
                el['radius'] = 'pill'
            elif e.get('shape') in ('roundrect', 'container') and e.get('radius', 0) >= 2:
                el['radius'] = e['radius']
    elif t == 'line':
        e = ents[0]
        x0, y0, x1, y1 = e['box']
        if (x1 - x0) >= (y1 - y0):
            ym = (y0 + y1) / 2
            el.setdefault('p1', [x0, ym])
            el.setdefault('p2', [x1, ym])
        else:
            xm = (x0 + x1) / 2
            el.setdefault('p1', [xm, y0])
            el.setdefault('p2', [xm, y1])
        el.setdefault('width', max(1, min(x1 - x0, y1 - y0)))
        el.setdefault('color', e.get('color'))
    elif t == 'image':
        e = ents[0]
        x0, y0, x1, y1 = e['box']
        pad = el.get('pad', 2)
        el.setdefault('box', [x0 - pad, y0 - pad, x1 + pad, y1 + pad])


def ink_metrics(font, text):
    x0, _, x1, _ = ink_extents(font, text)
    return x1 - x0, x0


def measuring_file(family, text, lang, bold=False, italic=False):
    """Font file to measure `text` with: the family (or its metric twin) when it can draw the text, else any
    installed font for the language. Returns (path, exact, resolved_family)."""
    path, exact, resolved = find_font_file(family, bold, italic)
    if profile(text)['family'] == 'alphabetic':
        return path, exact, resolved
    letters = [c for c in text if unicodedata.category(c)[0] == 'L']
    lacking = set(missing_glyphs(path, text)) if path else set(letters)
    if letters and sum(c in lacking for c in letters) > 0.2 * len(letters):
        alt = find_lang_font(lang, bold, italic)
        if alt[0]:
            return alt
        return (None, False, None) if not path else (path, False, resolved)
    return path, exact, resolved


def fit_text(el, slide_lang='en-US'):
    lines = element_lines(el)
    joined = ' '.join(lines)
    prof = profile(joined)
    lang = el.get('lang') or guess_lang(joined, slide_lang)
    rtl = is_rtl(el, slide_lang)
    fam = measuring_font(el.get('font', 'Arial'), joined, lang, el.get('font_ea'), el.get('font_cs'))
    path, exact, resolved = measuring_file(fam, joined, lang, el.get('bold', False), el.get('italic', False))
    fit = el.get('fit', {}) or {}
    mode = fit.get('mode', 'size')
    boxes = el.get('line_boxes') or []
    # sample line and its measured width: explicit fit.text/fit.w, else the longest line with its own width
    line_w, k = el.get('line_w') or [], None
    if fit.get('text'):
        sample, target_w = fit['text'], fit.get('w', el.get('w'))
    elif lines:
        k = max(range(len(lines)), key=lambda i: len(lines[i]))
        sample = lines[k]
        target_w = fit.get('w') or (line_w[k] if len(line_w) == len(lines) else el.get('w'))
    else:
        sample, target_w = '', None
    if k is not None and len(boxes) == len(lines):
        sample_box = boxes[k]
    else:
        sample_box = boxes[0] if len(boxes) == 1 else None
    cap_px = fit.get('cap', el.get('cap'))
    # full-width CJK text is one em per character in every CJK font: its width is exact with any of them, as
    # long as the font has the characters (a font without them draws boxes of its own width)
    trusted = bool(exact) or (prof['fullwidth'] and bool(path) and not missing_glyphs(path, joined))
    info = {'font': fam, 'font_file': os.path.basename(split_index(path)[0]) if path else None,
            'resolved': resolved, 'exact': trusted, 'lang': lang, 'script': prof['script']}
    font = load_font(path, M) if path else None
    if font is not None and sample:
        m = measure(path, sample, M, lang, profile(sample), rtl)
        w200, h200 = m['x1'] - m['x0'], m['bottom'] - m['top']
        capr = None
        if prof['family'] == 'alphabetic':  # a substitute font's cap height says nothing about the wanted one
            hb = ink_extents(font, 'H')
            capr = (hb[3] - hb[1]) / M if exact else cap_ratio(fam)
        src_h = (sample_box[3] - sample_box[1]) if sample_box else None
        cores = el.get('line_core') or []
        src_core = None
        if k is not None and len(cores) == len(lines):
            src_core = cores[k][1] - cores[k][0]
        elif len(cores) == 1:
            src_core = cores[0][1] - cores[0][0]
        hls = el.get('line_headline') or []
        hl_src = hls[k] if (k is not None and len(hls) == len(lines)) else (hls[0] if len(hls) == 1 else None)
        size, method = el.get('size'), None
        if mode == 'spacing' and not prof['joined'] and trusted and m['width_ok'] and (capr and cap_px or src_h):
            size = cap_px / capr if (capr and cap_px) else M * src_h / h200
            method = 'cap+spacing' if (capr and cap_px) else 'height+spacing'
            if target_w:
                el['spacing'] = round((target_w - w200 * size / M) / max(1, len(sample) - 1), 3)
        elif trusted and m['width_ok'] and target_w:
            size, method = M * target_w / w200, 'width'
        elif prof['script'] in HEADLINE_SCRIPTS and hl_src and (bd := bands(path, sample, M, lang, profile(sample), rtl)) \
                and 'headline_top' in bd and bd['body_bottom'] > bd['headline_top']:
            # unshaped widths are wrong, but the headline-to-baseline height is the same shaped or not
            size, method = M * (hl_src[1] - hl_src[0]) / (bd['body_bottom'] - bd['headline_top']), 'headline'
        elif prof['family'] != 'alphabetic' and (src_core or src_h):
            # no trustworthy width: the letter-body band (rows >= 30 % of the densest) is the same shaped or not
            bd = bands(path, sample, M, lang, profile(sample), rtl) if src_core else None
            if bd and bd['core_bottom'] - bd['core_top'] > 0:
                size, method = M * src_core / (bd['core_bottom'] - bd['core_top']), 'body height'
            elif src_h and h200 > 0:
                size, method = M * src_h / h200, 'height'
        elif cap_px and capr:
            size, method = cap_px / capr, 'cap'
        elif src_h and h200 > 0:
            size, method = M * src_h / h200, 'height'
        if size:
            el['size'] = round(size, 2)
            sc = el['size'] / M
            el['lsb'] = round(m['x0'] * sc, 2)
            el['rsb'] = round((m['advance'] - m['x1']) * sc, 2)
            info['ink_w'] = round(w200 * sc, 2)
        info.update({'method': method, 'measure': m['method'], 'cap_ratio': round(capr, 3) if capr else None,
                     'sample': sample, 'target_w': target_w, 'n': len(sample)})
        lacking = missing_glyphs(path, joined)
        if lacking and exact:
            info['note'] = f"{resolved} has no glyph for {''.join(lacking[:8])}: PowerPoint will use another font there"
    else:
        if cap_px and not fit.get('keep_size'):
            el['size'] = round(cap_px / cap_ratio(fam), 2)
        info['note'] = 'font not available here: size estimated from the cap height'
    # A block's lines start at different ink offsets (a line opening with "（" or "W"): put the box edge where
    # every line's ink, with its own side bearing, says it is, then express it against x.
    if el.get('size') and font is not None and len(boxes) == len(lines) > 1 and el.get('x') is not None:
        sc, edges = el['size'] / M, []
        side = 'left' if el['type'] == 'bullets' and not rtl else 'right' if el['type'] == 'bullets' \
            else el.get('align') or ('right' if rtl else 'left')
        if side in ('left', 'right'):
            for ln, b in zip(lines, boxes):
                mi = measure(path, ln, M, lang, profile(ln), rtl)
                edges.append(b[0] - mi['x0'] * sc if side == 'left' else b[2] + (mi['advance'] - mi['x1']) * sc)
            edge = sorted(edges)[len(edges) // 2]
            anchor = el['text_x'] if el['type'] == 'bullets' else el['x']
            if side == 'left':
                el['lsb'] = round(anchor - edge, 2)
            else:
                el['rsb'] = round(edge - anchor, 2)
    # The analysis "baseline" is the bottom of the densest band of ink rows: right for Latin, Cyrillic and Greek.
    # Headline scripts sit on the bottom of their letter bodies. For the others (Indic, Arabic and Hebrew words
    # with descending letters, Thai) find where the densest band falls for this text in this font, shift by it.
    if el.get('size') and font is not None and lines and el.get('baseline_from') == 'analysis' \
            and prof['family'] in ('indic', 'arabic', 'hebrew', 'sea'):
        bd = bands(path, lines[0], M, lang, profile(lines[0]), rtl)
        if bd and prof['family'] != 'indic' and bd['method'] not in ('raqm', 'arabic-joiner', 'basic'):
            bd = None  # drawn unjoined here: its row profile would mislead
        hl0 = (el.get('line_headline') or [None])[0]
        if bd and prof['script'] in HEADLINE_SCRIPTS and hl0 and 'body_bottom' in bd:
            el['baseline_src'], el['band_em'] = hl0[1], round(bd['body_bottom'] / M, 4)
            el['baseline_from'] = 'headline'
        elif bd:
            el['baseline_src'], el['band_em'] = el['baseline'], round(bd['dense_bottom'] / M, 4)
            el['baseline_from'] = 'dense band'
        if 'band_em' in el:
            el['baseline'] = round(el['baseline_src'] - el['band_em'] * el['size'], 2)
    # CJK fills its em box (the densest band is unstable on small type), and a G# reference has no baseline:
    # put the font's ink box where the source's is
    if el.get('size') and font is not None and boxes and lines and (
            'baseline' not in el or (prof['family'] == 'cjk' and el.get('baseline_from') == 'analysis')):
        m0 = measure(path, lines[0], M, lang, profile(lines[0]), rtl)
        b = boxes[0]
        el['baseline_src'], el['band_em'] = (b[1] + b[3]) / 2, round((m0['top'] + m0['bottom']) / 2 / M, 4)
        el['baseline'] = round(el['baseline_src'] - el['band_em'] * el['size'], 2)
        el['baseline_from'] = 'ink box'
    if 'baseline' not in el and boxes:
        el['baseline'] = round(boxes[0][1] + 0.8 * (boxes[0][3] - boxes[0][1]), 2)
    if not el.get('size'):
        info['note'] = 'NO SIZE: give "size", a measured width "w", a cap height "cap" or a "from" reference'
    if el['type'] == 'bullets':
        bp, bexact, _ = find_font_file(el.get('bullet_font', 'Arial'))
        bf = load_font(bp, M) if bp else None
        if bf is not None and el.get('size'):
            ch = el.get('bullet', '•')
            bx0, _, bx1, _ = ink_extents(bf, ch)
            k_ = el['size'] * el.get('bullet_size', 100) / 100 / M
            el['bullet_lsb'] = round(bx0 * k_, 2)
            el['bullet_rsb'] = round((bf.getlength(ch) - bx1) * k_, 2)
        if font is not None and el.get('size') and lines:
            m1 = measure(path, lines[0], M, lang, profile(lines[0]), rtl)
            el.setdefault('lsb', round(m1['x0'] * el['size'] / M, 2))
            el.setdefault('rsb', round((m1['advance'] - m1['x1']) * el['size'] / M, 2))
    el['fitted'] = info
    return el


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('--analysis', default=None)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    spec = load_json(a.spec)
    an_path = a.analysis or spec.get('analysis') or 'analysis.json'
    if not os.path.isabs(an_path) and not os.path.exists(an_path):
        an_path = os.path.join(os.path.dirname(os.path.abspath(a.spec)), an_path)
    idx = index_analysis(load_json(an_path)) if os.path.exists(an_path) else {}
    slide_lang = spec.get('lang', 'en-US')
    rows = []
    for el in spec['elements']:
        resolve(el, idx, slide_lang)
        if el['type'] in ('text', 'bullets') and not el.get('fixed'):
            fit_text(el, slide_lang)
            f = el['fitted']
            rows.append(f"{el.get('id', '?'):<18} {f.get('font', ''):<18} size {el.get('size', '?'):>7}  "
                        f"spacing {el.get('spacing', 0) or 0:>6}  {f.get('method') or '-':<13} "
                        f"{'exact' if f['exact'] else 'APPROX'}  {f.get('note', '')}")
    # one size per role (median), letter-spacing re-derived where the role is fitted in "spacing" mode
    roles = {}
    for el in spec['elements']:
        if el.get('role') and el['type'] in ('text', 'bullets') and el.get('size') and not el.get('fixed'):
            roles.setdefault(el['role'], []).append(el)
    for role, els in roles.items():
        if len(els) < 2:
            continue
        # sizes measured on the font PowerPoint will use outweigh estimates (substitute font, no shaping engine)
        trusted = [e for e in els if e.get('fitted', {}).get('exact') and e['fitted'].get('method') in MEASURED]
        pool = trusted or els
        med = sorted(e['size'] for e in pool)[len(pool) // 2]
        for el in els:
            f = med / el['size']
            el['size'] = round(med, 2)
            for key in ('lsb', 'rsb'):
                if key in el:
                    el[key] = round(el[key] * f, 2)
            fi = el.get('fitted', {})
            if (el.get('fit') or {}).get('mode') == 'spacing' and fi.get('ink_w') and fi.get('target_w'):
                fi['ink_w'] = round(fi['ink_w'] * f, 2)
                el['spacing'] = round((fi['target_w'] - fi['ink_w']) / max(1, fi.get('n', 2) - 1), 3)
            if 'band_em' in el:  # the dense-band shift scales with the size
                el['baseline'] = round(el['baseline_src'] - el['band_em'] * el['size'], 2)
        rows.append(f"role {role}: one size {med} for {len(els)} elements"
                    + (f" (median of the {len(pool)} measured on their own font)" if len(pool) < len(els) else ''))
    out = a.out or a.spec.replace('.json', '.fitted.json')
    save_json(spec, out)
    print('\n'.join(rows))
    print('->', out)


if __name__ == '__main__':
    main()
