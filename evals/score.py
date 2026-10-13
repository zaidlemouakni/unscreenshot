"""Score a rebuilt slide against an example's reference, deterministically (no AI judge).

    python evals/score.py <example> <slide.pptx> [<slide.pptx>...] [--json out.json]

The reference is the example's hand-made .pptx (validated in PowerPoint) and its source image.
Components, each 0..1:
  text     1 - character error rate: every reference text line against the closest stretch of rebuilt text
           (so splitting a block into one box per line, or not, does not matter)
  objects  1 - relative difference of the counts per kind: text lines, rectangles, arrows, ellipses, lines,
           pictures, bullets
  visual   edge F1 between the source image and a render of the rebuild (2 px tolerance), divided by the same
           F1 for the reference rebuild and capped at 1 (needs PowerPoint or LibreOffice)
score = 0.4 text + 0.2 objects + 0.4 visual   (0.6 text + 0.4 objects without a renderer)
"""
import argparse
import json
import os
import re
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'unscreenshot', 'scripts'))
from common import box_any  # noqa: E402

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
ARROWS = {'homePlate', 'chevron', 'rightArrow', 'notchedRightArrow', 'pentagon', 'leftArrow'}
KINDS = ('text', 'rect', 'arrow', 'ellipse', 'line', 'picture', 'bullet')


def norm(s):
    return ' '.join(unicodedata.normalize('NFC', s).split())


def slide_root(pptx, number=1):
    with zipfile.ZipFile(pptx) as z:
        return ET.fromstring(z.read(f'ppt/slides/slide{number}.xml'))


def text_lines(root):
    """Visible text lines: paragraphs, split at line breaks."""
    lines = []
    for p in root.iter(f'{A}p'):
        cur = ''
        for child in p:
            if child.tag in (f'{A}r', f'{A}fld'):
                cur += ''.join(t.text or '' for t in child.iter(f'{A}t'))
            elif child.tag == f'{A}br':
                lines.append(cur)
                cur = ''
        lines.append(cur)
    return [norm(x) for x in lines if x.strip()]


def inventory(root):
    n = dict.fromkeys(KINDS, 0)
    n['text'] = len(text_lines(root))
    n['bullet'] = sum(1 for p in root.iter(f'{A}pPr') if p.find(f'{A}buChar') is not None
                      or p.find(f'{A}buAutoNum') is not None)
    n['picture'] = sum(1 for _ in root.iter(f'{P}pic'))
    n['line'] = sum(1 for _ in root.iter(f'{P}cxnSp'))
    for sp in root.iter(f'{P}sp'):
        nv = sp.find(f'{P}nvSpPr/{P}cNvSpPr')
        if nv is not None and nv.get('txBox') == '1':
            continue
        geom = sp.find(f'{P}spPr/{A}prstGeom')
        prst = geom.get('prst') if geom is not None else 'custom'
        if prst in ('rect', 'roundRect', 'snip1Rect', 'round2SameRect'):
            # a plain rectangle holding only text, without fill or outline, is a text box
            sppr = sp.find(f'{P}spPr')
            filled = sppr is not None and (sppr.find(f'{A}solidFill') is not None or sppr.find(f'{A}gradFill') is not None
                                           or (sppr.find(f'{A}ln') is not None and sppr.find(f'{A}ln/{A}noFill') is None))
            if filled:
                n['rect'] += 1
        elif prst in ARROWS:
            n['arrow'] += 1
        elif prst == 'ellipse':
            n['ellipse'] += 1
        elif prst == 'line':
            n['line'] += 1
    return n


def substring_distance(needle, hay):
    """Edit distance from `needle` to the closest substring of `hay` (free start and end in hay)."""
    if not needle:
        return 0
    prev = [0] * (len(hay) + 1)
    for i, c in enumerate(needle, 1):
        cur = [i] + [0] * len(hay)
        for j, h in enumerate(hay, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (c != h))
        prev = cur
    return min(prev)


def text_score(ref_lines, got_lines):
    hay = ' ␞ '.join(got_lines)  # a separator no slide text contains: a match cannot span two lines freely
    total = sum(len(r) for r in ref_lines) or 1
    errors, worst = 0, []
    for r in ref_lines:
        d = substring_distance(r, hay)
        errors += d
        if d:
            worst.append((d, r))
    worst.sort(reverse=True)
    return max(0.0, 1 - errors / total), errors / total, [r for _, r in worst[:5]]


def objects_score(ref, got):
    diff = sum(abs(got[k] - ref[k]) for k in KINDS)
    return max(0.0, 1 - diff / max(1, sum(ref.values())))


def edges(gray):
    g = gray.astype(int)
    gx = np.zeros_like(g)
    gy = np.zeros_like(g)
    gx[:, 1:] = np.abs(np.diff(g, axis=1))
    gy[1:, :] = np.abs(np.diff(g, axis=0))
    return np.maximum(gx, gy) > 40


def edge_f1(src_gray, ren_gray, tol=2):
    es, er = edges(src_gray), edges(ren_gray)
    if not es.any() or not er.any():
        return 0.0
    precision = (er & box_any(es, tol, tol)).sum() / er.sum()
    recall = (es & box_any(er, tol, tol)).sum() / es.sum()
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def render(pptx, size, cache_dir):
    from check import render_libreoffice, render_powerpoint
    out = os.path.join(cache_dir, os.path.basename(pptx) + '.png')
    w, h = size
    path = render_libreoffice(pptx, w, out) or render_powerpoint(pptx, w, h, out)
    return Image.open(path).convert('L').resize(size, Image.LANCZOS) if path else None


def reference(example):
    d = os.path.join(ROOT, 'examples', example)
    pptx = next(os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith('.pptx'))
    return pptx, os.path.join(d, 'source.png')


def score(example, pptx, cache_dir, ref_visual=None):
    ref_pptx, src_png = reference(example)
    ref_root = slide_root(ref_pptx)
    result = {'example': example, 'pptx': pptx}
    if not os.path.isfile(pptx):
        return dict(result, score=0.0, error='no slide.pptx')
    try:
        got_root = slide_root(pptx)
    except Exception as ex:  # not a readable pptx
        return dict(result, score=0.0, error=f'unreadable pptx: {ex}')
    t, cer, worst = text_score(text_lines(ref_root), text_lines(got_root))
    ref_inv, got_inv = inventory(ref_root), inventory(got_root)
    o = objects_score(ref_inv, got_inv)
    result.update(text=round(t, 4), cer=round(cer, 4), worst_lines=worst, objects=round(o, 4),
                  inventory={'reference': ref_inv, 'rebuild': got_inv})
    src = Image.open(src_png).convert('L')
    ren = render(pptx, src.size, cache_dir)
    if ren is not None:
        if ref_visual is None:
            ref_ren = render(ref_pptx, src.size, cache_dir)
            ref_visual = edge_f1(np.asarray(src), np.asarray(ref_ren)) if ref_ren is not None else None
        f1 = edge_f1(np.asarray(src), np.asarray(ren))
        mad = float(np.abs(np.asarray(src, dtype=int) - np.asarray(ren, dtype=int)).mean())
        v = min(1.0, f1 / ref_visual) if ref_visual else f1
        result.update(visual=round(v, 4), edge_f1=round(f1, 4), reference_edge_f1=round(ref_visual or 0, 4),
                      mad=round(mad, 2), score=round(0.4 * t + 0.2 * o + 0.4 * v, 4))
    else:
        result.update(visual=None, score=round(0.6 * t + 0.4 * o, 4))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('example', choices=sorted(d for d in os.listdir(os.path.join(ROOT, 'examples'))
                                                if os.path.isdir(os.path.join(ROOT, 'examples', d))))
    ap.add_argument('pptx', nargs='+')
    ap.add_argument('--json')
    a = ap.parse_args()
    results = []
    with tempfile.TemporaryDirectory() as cache:
        for p in a.pptx:
            r = score(a.example, os.path.abspath(p), cache)
            results.append(r)
            keys = ('score', 'text', 'cer', 'objects', 'visual', 'mad')
            print(f"{a.example:<10} " + '  '.join(f'{k} {r.get(k)}' for k in keys if k in r)
                  + (f"  ERROR {r['error']}" if 'error' in r else '') + f'  {p}')
            if r.get('worst_lines'):
                print('   misread or missing:', ' | '.join(r['worst_lines'][:3]))
            if 'inventory' in r and r['inventory']['reference'] != r['inventory']['rebuild']:
                ref, got = r['inventory']['reference'], r['inventory']['rebuild']
                print('   objects (reference -> rebuild):', ', '.join(f'{k} {ref[k]}->{got[k]}' for k in KINDS
                                                                   if ref[k] != got[k]))
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
