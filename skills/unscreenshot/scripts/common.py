"""Shared helpers for the unscreenshot scripts. Hard dependencies: Pillow, numpy. Optional: scipy, fontTools."""
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFont

SLIDE_W_EMU = 12192000          # 13.333 in, standard 16:9 width
SLIDE_W_PT = 960.0

# Office fonts -> free fonts with identical metrics (same advance widths), used when the real font is absent.
METRIC_TWINS = {
    'arial': ['Liberation Sans', 'Arimo'],
    'arial narrow': ['Liberation Sans Narrow'],
    'times new roman': ['Liberation Serif', 'Tinos'],
    'courier new': ['Liberation Mono', 'Cousine'],
    'calibri': ['Carlito'],
    'cambria': ['Caladea'],
    'georgia': ['Gelasio'],
    'segoe ui': ['Selawik'],
    'segoe ui semibold': ['Selawik Semibold'],
    'century gothic': ['URW Gothic', 'URW Gothic L', 'TeX Gyre Adventor'],
    'century schoolbook': ['TeX Gyre Schola', 'C059', 'Century Schoolbook L'],
    'bookman old style': ['TeX Gyre Bonum', 'URW Bookman', 'URW Bookman L'],
}

# Windows file names (local runs only): regular, bold, italic, bold italic.
WIN_FILES = {
    'arial': ('arial.ttf', 'arialbd.ttf', 'ariali.ttf', 'arialbi.ttf'),
    'arial narrow': ('ARIALN.TTF', 'ARIALNB.TTF', 'ARIALNI.TTF', 'ARIALNBI.TTF'),
    'calibri': ('calibri.ttf', 'calibrib.ttf', 'calibrii.ttf', 'calibriz.ttf'),
    'cambria': ('cambria.ttc', 'cambriab.ttf', 'cambriai.ttf', 'cambriaz.ttf'),
    'century gothic': ('GOTHIC.TTF', 'GOTHICB.TTF', 'GOTHICI.TTF', 'GOTHICBI.TTF'),
    'segoe ui': ('segoeui.ttf', 'segoeuib.ttf', 'segoeuii.ttf', 'segoeuiz.ttf'),
    'segoe ui semibold': ('seguisb.ttf', 'seguisb.ttf', 'seguisbi.ttf', 'seguisbi.ttf'),
    'georgia': ('georgia.ttf', 'georgiab.ttf', 'georgiai.ttf', 'georgiaz.ttf'),
    'times new roman': ('times.ttf', 'timesbd.ttf', 'timesi.ttf', 'timesbi.ttf'),
    'verdana': ('verdana.ttf', 'verdanab.ttf', 'verdanai.ttf', 'verdanaz.ttf'),
    'tahoma': ('tahoma.ttf', 'tahomabd.ttf', 'tahoma.ttf', 'tahomabd.ttf'),
    'trebuchet ms': ('trebuc.ttf', 'trebucbd.ttf', 'trebucit.ttf', 'trebucbi.ttf'),
    'courier new': ('cour.ttf', 'courbd.ttf', 'couri.ttf', 'courbi.ttf'),
    'aptos': ('Aptos.ttf', 'Aptos-Bold.ttf', 'Aptos-Italic.ttf', 'Aptos-Bold-Italic.ttf'),
    # other scripts (no italics: PowerPoint slants the regular face)
    'yu gothic': ('YuGothR.ttc', 'YuGothB.ttc', 'YuGothR.ttc', 'YuGothB.ttc'),
    'microsoft yahei': ('msyh.ttc', 'msyhbd.ttc', 'msyh.ttc', 'msyhbd.ttc'),
    'microsoft yahei ui': ('msyh.ttc#1', 'msyhbd.ttc#1', 'msyh.ttc#1', 'msyhbd.ttc#1'),
    'microsoft jhenghei': ('msjh.ttc', 'msjhbd.ttc', 'msjh.ttc', 'msjhbd.ttc'),
    'microsoft jhenghei ui': ('msjh.ttc#1', 'msjhbd.ttc#1', 'msjh.ttc#1', 'msjhbd.ttc#1'),
    'ms gothic': ('msgothic.ttc',) * 4,
    'simsun': ('simsun.ttc',) * 4,
    'malgun gothic': ('malgun.ttf', 'malgunbd.ttf', 'malgun.ttf', 'malgunbd.ttf'),
    'nirmala ui': ('Nirmala.ttf', 'NirmalaB.ttf', 'Nirmala.ttf', 'NirmalaB.ttf'),
    'leelawadee ui': ('LeelawUI.ttf', 'LeelaUIb.ttf', 'LeelawUI.ttf', 'LeelaUIb.ttf'),
    'leelawadee': ('LEELAWAD.TTF', 'LEELAWDB.TTF', 'LEELAWAD.TTF', 'LEELAWDB.TTF'),
    'dubai': ('DUBAI-REGULAR.TTF', 'DUBAI-BOLD.TTF', 'DUBAI-REGULAR.TTF', 'DUBAI-BOLD.TTF'),
    'myanmar text': ('mmrtext.ttf', 'mmrtextb.ttf', 'mmrtext.ttf', 'mmrtextb.ttf'),
    'khmer ui': ('KhmerUI.ttf', 'KhmerUIb.ttf', 'KhmerUI.ttf', 'KhmerUIb.ttf'),
    'microsoft himalaya': ('himalaya.ttf',) * 4,
    'ebrima': ('ebrima.ttf', 'ebrimabd.ttf', 'ebrima.ttf', 'ebrimabd.ttf'),
}

# Office script fonts -> language to ask fontconfig for when they are absent (Linux sandboxes)
SCRIPT_FONT_LANG = {'yu gothic': 'ja', 'ms gothic': 'ja', 'meiryo': 'ja', 'microsoft yahei': 'zh-cn',
                    'microsoft yahei ui': 'zh-cn', 'simsun': 'zh-cn', 'dengxian': 'zh-cn', 'simhei': 'zh-cn',
                    'microsoft jhenghei': 'zh-tw', 'microsoft jhenghei ui': 'zh-tw', 'pmingliu': 'zh-tw',
                    'malgun gothic': 'ko', 'batang': 'ko', 'gulim': 'ko', 'nirmala ui': 'hi', 'mangal': 'hi',
                    'leelawadee ui': 'th', 'leelawadee': 'th', 'tahoma': 'th', 'dubai': 'ar', 'sakkal majalla': 'ar',
                    'myanmar text': 'my', 'khmer ui': 'km', 'microsoft himalaya': 'bo', 'ebrima': 'nqo'}

# First baseline / exact line spacing, measured in PowerPoint: 0.75 for every font tested (Latin, CJK, Indic,
# Thai, Arabic, Hebrew Office fonts) except these.
BASELINE_FACTOR = {'dubai': 0.725}

# Cap height / em, measured in PowerPoint. Used when the font file is not available.
CAP_RATIO = {
    'arial': 0.716, 'arial narrow': 0.716, 'calibri': 0.644, 'segoe ui': 0.700, 'segoe ui semibold': 0.700,
    'century gothic': 0.719,
    'aptos': 0.656, 'georgia': 0.692, 'cambria': 0.667, 'times new roman': 0.662, 'verdana': 0.727,
    'tahoma': 0.727, 'trebuchet ms': 0.715, 'courier new': 0.571, 'century schoolbook': 0.722,
    'bookman old style': 0.681,
    'yu gothic': 0.733, 'microsoft yahei': 0.75, 'microsoft jhenghei': 0.75, 'malgun gothic': 0.717,
    'nirmala ui': 0.70, 'leelawadee ui': 0.70, 'dubai': 0.65,
}
# Descent / em seen by PowerPoint when an exact line spacing is tighter than 1.25 x size (see notes).
TIGHT_DESCENT = {'arial': 0.225, 'segoe ui': 0.225, 'century gothic': 0.22, 'calibri': 0.25, 'aptos': 0.275}


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(obj, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))


def hex_to_rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(c):
    return '#%02X%02X%02X' % tuple(int(round(float(v))) for v in c[:3])


def load_rgb(path):
    return np.asarray(Image.open(path).convert('RGB'))


def box_any(mask, ry, rx):
    """Binary dilation of a bool mask with a (2ry+1) x (2rx+1) box, via an integral image."""
    if ry <= 0 and rx <= 0:
        return mask.copy()
    m = np.pad(mask.astype(np.int32), ((ry + 1, ry), (rx + 1, rx)))
    ii = m.cumsum(0).cumsum(1)
    h, w = mask.shape
    s = (ii[2 * ry + 1:2 * ry + 1 + h, 2 * rx + 1:2 * rx + 1 + w] - ii[:h, 2 * rx + 1:2 * rx + 1 + w]
         - ii[2 * ry + 1:2 * ry + 1 + h, :w] + ii[:h, :w])
    return s > 0


def box_all(mask, ry, rx):
    """Binary erosion (complement of the dilation of the complement)."""
    return ~box_any(~mask, ry, rx)


def _label_runs(mask):
    """8-connected labelling by run-length union-find (fallback when scipy is missing)."""
    h, w = mask.shape
    parent = [0]

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    lab = np.zeros((h, w), dtype=np.int32)
    prev = []
    for y in range(h):
        row = mask[y].astype(np.int8)
        d = np.diff(np.concatenate(([0], row, [0])))
        starts, ends = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
        cur, j = [], 0
        for s, e in zip(starts.tolist(), ends.tolist()):
            lbl = 0
            while j < len(prev) and prev[j][1] < s:
                j += 1
            k = j
            while k < len(prev) and prev[k][0] <= e:
                p = find(prev[k][2])
                if lbl == 0:
                    lbl = p
                elif p != lbl:
                    a, b = min(p, lbl), max(p, lbl)
                    parent[b] = a
                    lbl = a
                k += 1
            if lbl == 0:
                lbl = len(parent)
                parent.append(lbl)
            cur.append((s, e, lbl))
            lab[y, s:e] = lbl
        prev = cur
    roots = np.array([find(i) for i in range(len(parent))], dtype=np.int32)
    uniq, compact = np.unique(roots, return_inverse=True)
    compact = compact.astype(np.int32)
    if uniq[0] != 0:
        compact += 1
    return compact[lab], int(compact.max())


def label(mask):
    """Connected components (8-connectivity) -> (labels, count)."""
    try:
        from scipy import ndimage
        lab, n = ndimage.label(mask, structure=np.ones((3, 3), dtype=int))
        return lab, int(n)
    except Exception:
        return _label_runs(mask)


def objects(lab, n):
    """Bounding boxes [x0, y0, x1, y1] (inclusive) and pixel counts for labels 1..n."""
    ys, xs = np.nonzero(lab)
    ids = lab[ys, xs]
    x0 = np.full(n + 1, 1 << 30)
    y0 = np.full(n + 1, 1 << 30)
    x1 = np.full(n + 1, -1)
    y1 = np.full(n + 1, -1)
    np.minimum.at(x0, ids, xs)
    np.minimum.at(y0, ids, ys)
    np.maximum.at(x1, ids, xs)
    np.maximum.at(y1, ids, ys)
    cnt = np.bincount(ids, minlength=n + 1)
    return [(i, int(x0[i]), int(y0[i]), int(x1[i]), int(y1[i]), int(cnt[i])) for i in range(1, n + 1) if cnt[i]]


def headline_metrics(rows):
    """Lines hanging from a headline (Devanagari, Bengali, Gurmukhi): top of the headline (the first row at
    85 % of the densest) and bottom of the letter bodies below it (last row at 40 % of their median density),
    in fractional rows; the bottom of the bodies is the baseline. None when the profile is too short."""
    rows = np.asarray(rows, dtype=float)
    if len(rows) < 6 or rows.max() <= 0:
        return None
    mx = rows.max()
    top = int(np.argmax(rows >= 0.85 * mx))
    bot = top
    while bot + 1 < len(rows) and rows[bot + 1] >= 0.85 * mx:
        bot += 1
    below = rows[bot + 1:]
    if len(below) < 3 or not (below > 0).any():
        return None
    body = float(np.median(below[below > 0]))
    last = bot + 1 + int(np.flatnonzero(below >= 0.4 * body)[-1])
    ftop = top - (min(1.0, rows[top - 1] / rows[top]) if top > 0 else 0.0)  # partly covered row above
    nxt = rows[last + 1] if last + 1 < len(rows) else 0.0
    fbot = last + 1 + min(1.0, nxt / body) * (nxt < 0.4 * body)
    return float(ftop), float(fbot)


def local_background(rgb, cell):
    """Low-frequency background estimate: per-block median (text rarely covers half a block), then a 5x5
    median over blocks, upsampled. Robust inside dense bold titles and on coloured bars."""
    from PIL import ImageFilter
    h, w = rgb.shape[:2]
    c = max(2, int(cell))
    hc, wc = max(1, h // c), max(1, w // c)
    blk = rgb[:hc * c, :wc * c].reshape(hc, c, wc, c, 3)
    med = np.median(blk, axis=(1, 3)).astype(np.uint8)
    small = Image.fromarray(med).filter(ImageFilter.MedianFilter(5))
    return np.asarray(small.resize((w, h), Image.BILINEAR)).astype(np.int16)


def which(*names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    for p in (r'C:\Program Files\LibreOffice\program\soffice.exe', '/usr/bin/soffice', '/usr/lib/libreoffice/program/soffice',
              '/opt/libreoffice/program/soffice', '/Applications/LibreOffice.app/Contents/MacOS/soffice'):
        if os.path.basename(p).split('.')[0] in names and os.path.exists(p):
            return p
    return None


def powerpoint_available():
    """True on Windows when PowerPoint's COM server is registered (check.py can render with it)."""
    if os.name != 'nt' or not which('powershell'):
        return False
    try:
        import winreg
        winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'PowerPoint.Application\CLSID'))
        return True
    except OSError:
        return False


def split_index(path):
    """'fonts/x.ttc#1' -> ('fonts/x.ttc', 1): font files inside a collection carry their index after '#'."""
    base, sep, idx = (path or '').rpartition('#')
    return (base, int(idx)) if sep and idx.isdigit() else (path, 0)


def _fc_match(pattern):
    fc = shutil.which('fc-match')
    if not fc:
        return None
    try:
        out = subprocess.run([fc, '-f', '%{family}|%{file}|%{index}', pattern], capture_output=True, text=True,
                             timeout=20).stdout
        fam, path, idx = out.split('|', 2)
        path = path.strip() + (f'#{idx.strip()}' if idx.strip() not in ('', '0') else '')
        return fam.split(',')[0].strip(), path
    except Exception:
        return None


def find_font_file(family, bold=False, italic=False):
    """Locate a font file for `family`. Returns (path or None, metric_exact, resolved_family).

    The path may end with '#n' (font n of a .ttc collection): open it with load_font."""
    key = family.strip().lower()
    style = (':weight=200' if bold else ':weight=80') + (':slant=100' if italic else ':slant=0')
    for cand in [family] + METRIC_TWINS.get(key, []):
        res = _fc_match(cand + style)
        if res and res[0].lower() == cand.lower():
            return res[1], True, res[0]
    if key in WIN_FILES:
        idx = (2 if italic else 0) + (1 if bold else 0)
        dirs = [os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')]
        for d in dirs:
            name = WIN_FILES[key][idx]
            if os.path.exists(os.path.join(d, split_index(name)[0])):
                return os.path.join(d, name), True, family
    lang = SCRIPT_FONT_LANG.get(key)
    if lang:  # a font for the same language (Noto CJK, Noto Sans Arabic...): right script, other metrics
        res = _fc_match(f':lang={lang}' + style)
        if res:
            return res[1], False, res[0]
    res = _fc_match(family + style)
    if res:
        return res[1], False, res[0]
    return None, False, None


def fc_lang(lang):
    """BCP-47 tag -> fontconfig language ('zh-TW' -> 'zh-tw', 'ar-SA' -> 'ar')."""
    tag = (lang or '').lower()
    if tag.startswith('zh'):
        return 'zh-tw' if tag.startswith(('zh-tw', 'zh-hk', 'zh-mo', 'zh-hant')) else 'zh-cn'
    return tag.split('-')[0]


def find_lang_font(lang, bold=False, italic=False):
    """Any installed font for a language (Linux/macOS with fontconfig). Returns (path, False, family)."""
    style = (':weight=200' if bold else ':weight=80') + (':slant=100' if italic else ':slant=0')
    res = _fc_match(f':lang={fc_lang(lang)}' + style) if lang else None
    return (res[1], False, res[0]) if res else (None, False, None)


def load_font(path, size):
    p, idx = split_index(path)
    try:
        return ImageFont.truetype(p, size=size, index=idx)
    except Exception:
        return ImageFont.load_default(size=size) if hasattr(ImageFont, 'load_default') else None


def baseline_factor(family):
    return BASELINE_FACTOR.get((family or '').strip().lower(), 0.75)


def cap_ratio(family):
    return CAP_RATIO.get(family.strip().lower(), 0.70)


def ui_font(size=14):
    """A readable font for annotations."""
    for fam in ('DejaVu Sans', 'Liberation Sans', 'Arial'):
        p, _, _ = find_font_file(fam)
        if p:
            f = load_font(p, size)
            if f:
                return f
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def log(*a):
    print(*a, file=sys.stderr if os.environ.get('RS_QUIET') else sys.stdout)
