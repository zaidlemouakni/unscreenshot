"""Render the built PowerPoint and compare it with the source image.

    python scripts/check.py out/slide.pptx work/spec.fitted.json [--slide 2] [--render-png out/render.png] [--out out/check]

Rendering: --render-png if given, else LibreOffice (+ PyMuPDF / pypdfium2 / pdftoppm), else PowerPoint on
Windows. Writes in --out: render.png, side_by_side.png (source above, rebuild below), overlay.png
(black = both agree, cyan = only in the source, red = only in the rebuild), report.txt (per text element:
dx, baseline dy, width ratio) and spec.corrected.json (fixes worth applying). Rebuild from the corrected
spec and check again, three rounds at most.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import headline_metrics, load_json, powerpoint_available, save_json, which  # noqa: E402
from fit import element_lines, is_rtl  # noqa: E402
from textshape import HEADLINE_SCRIPTS, profile  # noqa: E402

# PowerPoint is single-instance: if the user already has it open, only close the presentation opened here.
PS_RENDER = r'''param([string]$Pptx, [string]$Png, [int]$W, [int]$H, [int]$Slide = 1)
$ErrorActionPreference = 'Stop'
$running = @(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$pp = New-Object -ComObject PowerPoint.Application
try { $p = $pp.Presentations.Open($Pptx, -1, 0, 0); $p.Slides.Item($Slide).Export($Png, 'PNG', $W, $H); $p.Close() }
finally { if (-not $running) { $pp.Quit() } }
'''


def render_libreoffice(pptx, width, out, slide=1):
    soffice = which('soffice', 'libreoffice')
    if not soffice:
        return None
    tmp = tempfile.mkdtemp(prefix='lo_')
    profile = 'file:///' + os.path.join(tmp, 'profile').replace('\\', '/').lstrip('/')
    subprocess.run([soffice, f'-env:UserInstallation={profile}', '--headless', '--convert-to', 'pdf',
                    '--outdir', tmp, pptx], check=True, timeout=240, capture_output=True)
    pdf = glob.glob(os.path.join(tmp, '*.pdf'))[0]
    dpi = width / 13.3333
    try:
        import fitz
        fitz.open(pdf)[slide - 1].get_pixmap(dpi=dpi).save(out)
    except ImportError:
        try:
            import pypdfium2 as pdfium
            pdfium.PdfDocument(pdf)[slide - 1].render(scale=dpi / 72).to_pil().save(out)
        except ImportError:
            subprocess.run([which('pdftoppm'), '-png', '-r', str(round(dpi)), '-f', str(slide), '-l', str(slide),
                            '-singlefile', pdf, out[:-4]], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def render_powerpoint(pptx, width, height, out, slide=1):
    if not powerpoint_available():
        return None
    ps = os.path.join(tempfile.mkdtemp(prefix='pp_'), 'render.ps1')
    with open(ps, 'w', encoding='utf-8') as f:
        f.write(PS_RENDER)
    r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps, '-Pptx',
                        os.path.abspath(pptx), '-Png', os.path.abspath(out), '-W', str(width), '-H', str(height),
                        '-Slide', str(slide)],
                       capture_output=True, timeout=240)
    return out if r.returncode == 0 and os.path.exists(out) else None


def ink(img, box):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    if x1 - x0 < 3 or y1 - y0 < 3:
        return None
    sub = img[y0:y1, x0:x1].astype(int)
    border = np.concatenate([sub[0], sub[-1], sub[:, 0], sub[:, -1]])
    d = np.abs(sub - np.median(border, axis=0)).max(axis=2)
    m = d > max(40, 0.4 * d.max())
    ys, xs = np.nonzero(m)
    if len(ys) < 8:
        return None
    return {'x0': x0 + xs.min(), 'x1': x0 + xs.max() + 1, 'y0': y0 + ys.min(), 'y1': y0 + ys.max() + 1, 'mask': m,
            'oy': y0}


def baseline(info, top, bottom, headline=False):
    """Bottom of the densest band of rows; for headline scripts (Devanagari...) the bottom of the letter
    bodies under the headline, the same measure fit.py places them with."""
    m = info['mask']
    a, b = max(0, int(top - info['oy'])), max(1, int(bottom - info['oy']))
    rows = m[a:b].sum(axis=1).astype(float)
    if not len(rows) or rows.max() == 0:
        return None
    if headline:
        hl = headline_metrics(rows)
        if hl:
            return info['oy'] + a + hl[1]
    dense = np.flatnonzero(rows >= 0.5 * rows.max())
    return info['oy'] + a + dense[-1] + 1


def text_box(el, slide_lang='en-US'):
    S = el['size']
    n = len(el.get('lines') or []) or 1
    if el['type'] == 'bullets':
        n = sum(len(i) if isinstance(i, list) else 1 for i in el['items'])
    pitch = el.get('pitch') or 1.3 * S
    w = el.get('w') or 0.6 * S * 30
    rtl = is_rtl(el, slide_lang)
    align = el.get('align') or ('right' if rtl else 'left')
    x = el['x']
    if el['type'] == 'bullets':  # from the bullet to the far end of the text, on either side
        left, right = (el['text_x'] - w, x) if rtl else (x, el['text_x'] + w)
    else:
        left = x if align == 'left' else x - w if align == 'right' else x - w / 2
        right = left + w
    return [left - 0.35 * S, el['baseline'] - 1.05 * S, right + 0.35 * S, el['baseline'] + (n - 1) * pitch + 0.4 * S]


def anchor_side(el, slide_lang):
    """The edge a text is anchored on: its x is that edge, so that is where its error is measured."""
    rtl = is_rtl(el, slide_lang)
    if el['type'] == 'bullets':
        return 'right' if rtl else 'left'
    return el.get('align') or ('right' if rtl else 'left')


def scale_size(el, f):
    el['size'] = round(el['size'] * f, 2)
    for k in ('lsb', 'rsb', 'bullet_lsb', 'bullet_rsb'):
        if k in el:
            el[k] = round(el[k] * f, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx')
    ap.add_argument('spec')
    ap.add_argument('--render-png', default=None)
    ap.add_argument('--renderer', default=None, help='libreoffice | powerpoint (how strict vertical fixes are)')
    ap.add_argument('--slide', type=int, default=1, help='slide number in the .pptx (1 = first)')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    spec = load_json(a.spec)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.pptx)), 'check')
    os.makedirs(out, exist_ok=True)
    spec_dir = os.path.dirname(os.path.abspath(a.spec))
    src_path = spec.get('source') or 'source.png'
    for cand in (os.path.join(spec_dir, src_path), src_path, os.path.join(spec_dir, os.path.basename(src_path))):
        if os.path.exists(cand):
            src_path = os.path.abspath(cand)
            break
    spec['source'] = src_path  # absolute in spec.corrected.json, which is written to another folder
    if spec.get('analysis') and not os.path.isabs(spec['analysis']):
        spec['analysis'] = os.path.abspath(os.path.join(spec_dir, spec['analysis']))
    src_img = Image.open(src_path).convert('RGB')
    W, H = src_img.size
    rpath, renderer = a.render_png, a.renderer or 'given'
    if not rpath:
        rpath = render_libreoffice(a.pptx, W, os.path.join(out, 'render_raw.png'), a.slide)
        renderer = 'libreoffice'
        if not rpath:
            rpath = render_powerpoint(a.pptx, W, H, os.path.join(out, 'render_raw.png'), a.slide)
            renderer = 'powerpoint'
    if not rpath:
        sys.exit('No renderer available (LibreOffice or PowerPoint): pass --render-png, or compare visually.')
    ren_img = Image.open(rpath).convert('RGB').resize((W, H), Image.LANCZOS)
    ren_img.save(os.path.join(out, 'render.png'))
    src, ren = np.asarray(src_img), np.asarray(ren_img)

    both = Image.new('RGB', (W, H * 2 + 8), (255, 0, 0))
    both.paste(src_img, (0, 0))
    both.paste(ren_img, (0, H + 8))
    both.save(os.path.join(out, 'side_by_side.png'))
    gs, gr = np.asarray(src_img.convert('L')), np.asarray(ren_img.convert('L'))
    Image.fromarray(np.dstack([gr, gs, gs]).astype(np.uint8)).save(os.path.join(out, 'overlay.png'))
    mad = float(np.abs(gs.astype(int) - gr.astype(int)).mean())

    slide_lang = spec.get('lang', 'en-US')
    lines, fixes, rows = [], 0, []
    for el in spec['elements']:
        if el['type'] not in ('text', 'bullets') or not el.get('size') or el.get('skip'):
            continue
        box = text_box(el, slide_lang)
        s, r = ink(src, box), ink(ren, box)
        name = el.get('id', '?')
        if not s or not r:
            lines.append(f"{name:<24} not measurable (no text found in {[round(v) for v in box]})")
            continue
        S = el['size']
        prof = profile(' '.join(element_lines(el)))
        hl = prof['script'] in HEADLINE_SCRIPTS
        sb = baseline(s, el['baseline'] - 1.05 * S, el['baseline'] + 0.3 * S, hl)
        rb = baseline(r, el['baseline'] - 1.05 * S, el['baseline'] + 0.3 * S, hl)
        side = anchor_side(el, slide_lang)
        if side == 'right':
            dx = float(r['x1'] - s['x1'])
        elif side == 'center':
            dx = float(round((r['x0'] + r['x1'] - s['x0'] - s['x1']) / 2))
        else:
            dx = float(r['x0'] - s['x0'])
        dy = float(round(rb - sb)) if (sb is not None and rb is not None) else 0.0
        if prof['family'] == 'cjk' and len(el.get('lines') or []) <= 1:  # CJK fills its em box: compare ink boxes
            dy = float(round((r['y0'] + r['y1'] - s['y0'] - s['y1']) / 2))
        wr = float((s['x1'] - s['x0']) / max(1, r['x1'] - r['x0']))
        if abs(wr - 1) > 0.12 or abs(dx) > 0.5 * S or abs(dy) > 0.5 * S:
            lines.append(f"{name:<24} dx {dx:+5.1f}  dy {dy:+5.1f}  width x{wr:.3f}  "
                         "?? suspicious (another shape inside the area?) -> check overlay.png, nothing applied")
            continue
        rows.append((el, s, r, dx, dy, wr, prof))
    # One size per role. When every member of a role renders too narrow (or too wide), the shared size is off:
    # scale them together, so they stay equal.
    by_role, role_scale = {}, {}
    for el, s, r, dx, dy, wr, prof in rows:
        if el.get('role') and (el.get('fit') or {}).get('mode') != 'spacing':
            by_role.setdefault(el['role'], []).append((el, wr))
    for role, members in by_role.items():
        ws = sorted(w for _, w in members)
        med = ws[len(ws) // 2]
        same_way = min(ws) > 1 or max(ws) < 1
        if len(ws) >= 2 and abs(med - 1) >= 0.015 and same_way and all(
                (e.get('fitted') or {}).get('exact') for e, _ in members):
            role_scale[role] = med
    for el, s, r, dx, dy, wr, prof in rows:
        name, S, acts = el.get('id', '?'), el['size'], []
        if abs(dx) >= 1.5:
            el['x'] = round(el['x'] - dx, 2)
            if el['type'] == 'bullets':
                el['text_x'] = round(el['text_x'] - dx, 2)
            acts.append(f'x{-dx:+.0f}')
        vlim = 1.5 if renderer in ('powerpoint', 'given') else max(3.0, 0.12 * S)
        if abs(dy) >= vlim:
            el['baseline'] = round(el['baseline'] - dy, 2)
            acts.append(f'baseline{-dy:+.0f}')
        gap = abs((s['x1'] - s['x0']) - (r['x1'] - r['x0']))
        if el.get('role') and (el.get('fit') or {}).get('mode') != 'spacing':
            if el['role'] in role_scale:
                scale_size(el, role_scale[el['role']])
                acts.append(f"role size x{role_scale[el['role']]:.3f}")
        elif gap < 2:
            pass  # 1 px is the measuring resolution: on short texts it would grow the size every round
        elif (el.get('fitted') or {}).get('exact') and abs(wr - 1) >= 0.015 and el['type'] == 'text':
            if (el.get('fit') or {}).get('mode') == 'spacing' and not prof['joined']:
                n = (el.get('fitted') or {}).get('n', 2)
                el['spacing'] = round((el.get('spacing') or 0) + ((s['x1'] - s['x0']) - (r['x1'] - r['x0'])) / max(1, n - 1), 3)
                acts.append('spacing')
            else:
                scale_size(el, wr)
                acts.append(f'size x{wr:.3f}')
        fixes += bool(acts)
        lines.append(f"{name:<24} dx {dx:+5.1f}  dy {dy:+5.1f}  width x{wr:.3f}  {' '.join(acts) or 'ok'}")
    rep = [f'Renderer: {renderer}  |  mean luminance difference: {mad:.2f}/255', ''] + lines + \
          ['', f'{fixes} element(s) to fix -> spec.corrected.json' if fixes else 'No correction needed.']
    with open(os.path.join(out, 'report.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(rep))
    save_json(spec, os.path.join(out, 'spec.corrected.json'))
    print('\n'.join(rep))
    print('->', out)


if __name__ == '__main__':
    main()
