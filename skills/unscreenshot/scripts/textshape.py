"""Writing systems: which script a text is in, its direction, its PowerPoint font slots, and how to measure it.

Measured in PowerPoint (2026-10):
- a run's characters use one of three font slots: CJK (Han, kana, hangul) the East Asian font `ea`; Arabic,
  Hebrew, Thai and the Indic scripts the complex-script font `cs`; everything else (Latin incl. Vietnamese,
  Cyrillic, Greek) the Latin font;
- `algn` stays visual (l / ctr / r) in right-to-left paragraphs; a right-to-left paragraph without `algn` is
  right-aligned; right-to-left bullets need rtl="1" + algn="r" (marL / indent then count from the right);
- letter-spacing breaks Arabic joins and the Devanagari headline: never letter-space joined scripts;
- the first-baseline rule (0.75 x exact line spacing) holds for the CJK, Indic, Thai, Arabic and Hebrew Office
  fonts within 1 px, except Dubai (see common.BASELINE_FACTOR).

Widths of joined and complex scripts need shaping: Pillow's raqm layout when available, otherwise a built-in
Arabic joiner (presentation forms derived from the Unicode database), otherwise the caller fits on the ink
height of the exact text (`width_ok` False).
"""
import os
import sys
import unicodedata
from functools import lru_cache

from PIL import ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import headline_metrics, split_index  # noqa: E402

# first word of the Unicode character name -> script family
FAMILIES = {
    'LATIN': 'alphabetic', 'CYRILLIC': 'alphabetic', 'GREEK': 'alphabetic', 'ARMENIAN': 'alphabetic',
    'GEORGIAN': 'alphabetic', 'CJK': 'cjk', 'HIRAGANA': 'cjk', 'KATAKANA': 'cjk', 'KATAKANA-HIRAGANA': 'cjk',
    'HANGUL': 'cjk', 'BOPOMOFO': 'cjk', 'IDEOGRAPHIC': 'cjk', 'FULLWIDTH': 'cjk', 'HALFWIDTH': 'cjk',
    'ARABIC': 'arabic', 'SYRIAC': 'arabic', 'NKO': 'arabic', 'HEBREW': 'hebrew', 'THAANA': 'hebrew',
    'DEVANAGARI': 'indic', 'BENGALI': 'indic', 'GURMUKHI': 'indic', 'GUJARATI': 'indic', 'ORIYA': 'indic',
    'TAMIL': 'indic', 'TELUGU': 'indic', 'KANNADA': 'indic', 'MALAYALAM': 'indic', 'SINHALA': 'indic',
    'THAI': 'sea', 'LAO': 'sea', 'KHMER': 'sea', 'MYANMAR': 'sea', 'TIBETAN': 'sea',
}
SLOT = {'alphabetic': 'latin', 'cjk': 'ea', 'arabic': 'cs', 'hebrew': 'cs', 'indic': 'cs', 'sea': 'cs'}
JOINED = {'arabic', 'indic'}
# scripts whose widths are wrong without a shaping engine (reordering, conjuncts, stacking)
NEEDS_SHAPING = {'indic'}
NEEDS_SHAPING_SCRIPTS = {'KHMER', 'MYANMAR', 'TIBETAN'}
# letters hang from a headline: the densest rows are the headline, the baseline is the bottom of the bodies
HEADLINE_SCRIPTS = {'DEVANAGARI', 'BENGALI', 'GURMUKHI'}

# primary language subtag -> family, to tell whether the slide language fits a run
LANG_FAMILY = {'ar': 'arabic', 'fa': 'arabic', 'ur': 'arabic', 'ps': 'arabic', 'ug': 'arabic', 'ku': 'arabic',
               'he': 'hebrew', 'yi': 'hebrew', 'dv': 'hebrew', 'zh': 'cjk', 'ja': 'cjk', 'ko': 'cjk',
               'hi': 'indic', 'mr': 'indic', 'ne': 'indic', 'sa': 'indic', 'bn': 'indic', 'as': 'indic',
               'pa': 'indic', 'gu': 'indic', 'or': 'indic', 'ta': 'indic', 'te': 'indic', 'kn': 'indic',
               'ml': 'indic', 'si': 'indic', 'th': 'sea', 'lo': 'sea', 'km': 'sea', 'my': 'sea', 'bo': 'sea'}
SCRIPT_LANG = {'ARABIC': 'ar-SA', 'HEBREW': 'he-IL', 'HANGUL': 'ko-KR', 'HIRAGANA': 'ja-JP', 'KATAKANA': 'ja-JP',
               'KATAKANA-HIRAGANA': 'ja-JP', 'CJK': 'zh-CN', 'IDEOGRAPHIC': 'zh-CN', 'DEVANAGARI': 'hi-IN',
               'BENGALI': 'bn-IN', 'GURMUKHI': 'pa-IN', 'GUJARATI': 'gu-IN', 'ORIYA': 'or-IN', 'TAMIL': 'ta-IN',
               'TELUGU': 'te-IN', 'KANNADA': 'kn-IN', 'MALAYALAM': 'ml-IN', 'SINHALA': 'si-LK', 'THAI': 'th-TH',
               'LAO': 'lo-LA', 'KHMER': 'km-KH', 'MYANMAR': 'my-MM', 'TIBETAN': 'bo-CN', 'CYRILLIC': 'ru-RU',
               'GREEK': 'el-GR', 'ARMENIAN': 'hy-AM', 'GEORGIAN': 'ka-GE', 'SYRIAC': 'syr-SY', 'THAANA': 'dv-MV'}
PERSIAN_LETTERS = set('پچژگکی')
URDU_LETTERS = set('ٹڈڑںےھ')
CYRILLIC_LANGS = {'ru', 'uk', 'bg', 'sr', 'mk', 'be', 'kk', 'ky', 'mn', 'tg', 'tt'}


def is_vietnamese(chars):
    """Letters found only in Vietnamese: ă đ ơ ư and the stacked tone marks of U+1EA0-U+1EF9."""
    return any(c in 'ăđơưĂĐƠƯ' or 0x1EA0 <= ord(c) <= 0x1EF9 for c in chars)

# Office fonts per script, used when the spec does not name one (Windows / Office defaults)
EA_DEFAULT = {'ja': 'Yu Gothic', 'ko': 'Malgun Gothic', 'zh': 'Microsoft YaHei', 'zh-hant': 'Microsoft JhengHei'}
CS_DEFAULT = {'ARABIC': 'Segoe UI', 'HEBREW': 'Segoe UI', 'THAI': 'Leelawadee UI', 'LAO': 'Leelawadee UI',
              'KHMER': 'Khmer UI', 'MYANMAR': 'Myanmar Text', 'TIBETAN': 'Microsoft Himalaya', 'NKO': 'Ebrima',
              'SYRIAC': 'Segoe UI Historic', 'THAANA': 'MV Boli'}
CS_DEFAULT_INDIC = 'Nirmala UI'
# Office fonts that also draw these families, so they can stay in their slot
CS_CAPABLE = {'segoe ui': {'arabic', 'hebrew'}, 'segoe ui semibold': {'arabic', 'hebrew'},
              'segoe ui light': {'arabic', 'hebrew'}, 'arial': {'arabic', 'hebrew'},
              'times new roman': {'arabic', 'hebrew'}, 'courier new': {'arabic', 'hebrew'},
              'tahoma': {'arabic', 'hebrew', 'sea'}, 'microsoft sans serif': {'arabic', 'hebrew', 'sea'},
              'dubai': {'arabic'}, 'sakkal majalla': {'arabic'}, 'traditional arabic': {'arabic'},
              'simplified arabic': {'arabic'}, 'arabic typesetting': {'arabic'}, 'david': {'hebrew'},
              'nirmala ui': {'indic'}, 'mangal': {'indic'}, 'kokila': {'indic'}, 'leelawadee ui': {'sea'},
              'leelawadee': {'sea'}, 'cordia new': {'sea'}, 'angsana new': {'sea'}, 'browallia new': {'sea'}}
EA_CAPABLE = {'yu gothic', 'yu gothic ui', 'yu mincho', 'meiryo', 'meiryo ui', 'ms gothic', 'ms pgothic',
              'ms mincho', 'microsoft yahei', 'microsoft yahei ui', 'dengxian', 'simsun', 'simhei', 'kaiti',
              'fangsong', 'microsoft jhenghei', 'microsoft jhenghei ui', 'pmingliu', 'mingliu', 'malgun gothic',
              'batang', 'gulim', 'dotum', 'gungsuh', 'noto sans cjk jp', 'noto sans cjk sc', 'noto sans cjk tc',
              'noto sans cjk kr', 'source han sans'}


def char_script(ch):
    name = unicodedata.name(ch, '')
    return name.split(' ')[0] if name else ''


def profile(text):
    """Dominant script family of `text`, its direction, font slot and measuring needs."""
    counts, scripts = {}, {}
    rtl = ltr = 0
    for ch in text:
        if unicodedata.category(ch)[0] in 'LM':
            sc = char_script(ch)
            fam = FAMILIES.get(sc)
            if fam:
                counts[fam] = counts.get(fam, 0) + 1
                scripts[sc] = scripts.get(sc, 0) + 1
        bd = unicodedata.bidirectional(ch)
        if bd in ('R', 'AL'):
            rtl += 1
        elif bd == 'L':
            ltr += 1
    fam = max(counts, key=counts.get) if counts else 'alphabetic'
    script = max(scripts, key=scripts.get) if scripts else 'LATIN'
    body = text.strip()
    return {'family': fam, 'script': script, 'families': sorted(counts), 'scripts': sorted(scripts),
            'rtl': rtl > ltr, 'joined': fam in JOINED, 'slot': SLOT[fam],
            # Han, kana and full-width punctuation are one em wide in every CJK font
            'fullwidth': bool(body) and all(unicodedata.east_asian_width(c) in ('W', 'F') for c in body)
            and 'HANGUL' not in scripts}


def guess_lang(text, default='en-US'):
    """BCP-47 tag for a run: the slide language when it fits the run's script, else one guessed from it."""
    default = default or 'en-US'
    if not any(unicodedata.category(c)[0] == 'L' for c in text):
        return default  # digits, punctuation: the slide language
    prof = profile(text)
    primary = default.split('-')[0].lower()
    chars = set(text)
    fam, scripts = prof['family'], set(prof['scripts'])
    fits = LANG_FAMILY.get(primary, 'alphabetic') == fam
    if fits and fam == 'cjk':
        kana = {'HIRAGANA', 'KATAKANA', 'KATAKANA-HIRAGANA'} & scripts
        fits = not ((kana and primary != 'ja') or ('HANGUL' in scripts and primary != 'ko'))
    elif fits and fam == 'arabic':
        fits = not (chars & (PERSIAN_LETTERS | URDU_LETTERS)) or primary in ('fa', 'ur', 'ps', 'ku', 'ug')
    elif fits and fam == 'alphabetic':
        fits = ((primary in CYRILLIC_LANGS) == (prof['script'] == 'CYRILLIC')
                and (primary == 'el') == (prof['script'] == 'GREEK')
                and (primary == 'vi') == is_vietnamese(chars))
    if fits:
        return default
    if fam == 'cjk':  # kana means Japanese, hangul Korean, Han alone Chinese (simplified unless told)
        if scripts & {'HIRAGANA', 'KATAKANA', 'KATAKANA-HIRAGANA'}:
            return 'ja-JP'
        return 'ko-KR' if 'HANGUL' in scripts else 'zh-CN'
    if prof['script'] == 'ARABIC':
        return 'ur-PK' if chars & URDU_LETTERS else 'fa-IR' if chars & PERSIAN_LETTERS else 'ar-SA'
    if prof['script'] == 'LATIN':
        return 'vi-VN' if is_vietnamese(chars) else 'en-US'
    return SCRIPT_LANG.get(prof['script'], default)


def ea_default(text, lang=None):
    tag = (lang or '').lower()
    if tag.startswith(('zh-tw', 'zh-hk', 'zh-mo', 'zh-hant')):
        return EA_DEFAULT['zh-hant']
    for k in ('ja', 'ko', 'zh'):
        if tag.startswith(k):
            return EA_DEFAULT[k]
    scripts = set(profile(text)['scripts'])
    if scripts & {'HIRAGANA', 'KATAKANA', 'KATAKANA-HIRAGANA'}:
        return EA_DEFAULT['ja']
    if 'HANGUL' in scripts:
        return EA_DEFAULT['ko']
    return EA_DEFAULT['zh']


def cs_default(text):
    counts = {}
    for ch in text:
        sc = char_script(ch)
        if SLOT.get(FAMILIES.get(sc, ''), '') == 'cs':
            counts[sc] = counts.get(sc, 0) + 1
    if not counts:
        return None
    sc = max(counts, key=counts.get)
    return CS_DEFAULT.get(sc) or (CS_DEFAULT_INDIC if FAMILIES[sc] == 'indic' else 'Segoe UI')


def slot_fonts(font, text, lang=None, font_ea=None, font_cs=None):
    """{'latin', 'ea', 'cs'} typefaces for a run: the spec's font where it can draw the text, else the Office
    default for the script (East Asian fonts by language, complex scripts by script)."""
    font = font or 'Arial'
    key = font.strip().lower()
    prof = profile(text)
    ea = font_ea or (font if key in EA_CAPABLE else None)
    if not ea:
        ea = ea_default(text, lang) if 'cjk' in prof['families'] else font
    cs = font_cs
    if not cs:
        need = {f for f in prof['families'] if SLOT[f] == 'cs'}
        cs = font if not need or need <= CS_CAPABLE.get(key, set()) else cs_default(text)
    return {'latin': font, 'ea': ea, 'cs': cs}


def measuring_font(el_font, text, lang=None, font_ea=None, font_cs=None):
    """The typeface that draws most of `text` in PowerPoint (the one to measure)."""
    return slot_fonts(el_font, text, lang, font_ea, font_cs)[profile(text)['slot']]


# ------------------------------------------------------------------ Arabic joining (for measuring only)
@lru_cache(maxsize=1)
def _arabic_forms():
    """Contextual forms from the Unicode presentation-form blocks: base letter -> {isolated, final, initial,
    medial}, and lam + alef -> ligature forms."""
    forms, ligs = {}, {}
    for cp in list(range(0xFB50, 0xFE00)) + list(range(0xFE70, 0xFF00)):
        ch = chr(cp)
        dec = unicodedata.decomposition(ch)
        if not dec.startswith('<'):
            continue
        tag, _, rest = dec.partition('> ')
        tag = tag[1:]
        if tag not in ('isolated', 'final', 'initial', 'medial'):
            continue
        bases = tuple(chr(int(h, 16)) for h in rest.split())
        if len(bases) == 1:
            forms.setdefault(bases[0], {}).setdefault(tag, ch)
        elif len(bases) == 2 and bases[0] == 'ل' and bases[1] in 'آأإا':
            ligs.setdefault(bases, {}).setdefault(tag, ch)
    return forms, ligs


def _joining(ch, forms):
    if ch in ('ـ', '‍'):          # tatweel, zero width joiner: join on both sides
        return 'C'
    if unicodedata.category(ch) in ('Mn', 'Me', 'Cf') and ch != '‌':
        return 'T'                            # harakat and other marks: transparent
    f = forms.get(ch)
    if not f:
        return 'U'
    if 'initial' in f or 'medial' in f:
        return 'D'
    return 'R' if 'final' in f else 'U'


def arabic_shape(text):
    """Replace Arabic-script letters by their contextual presentation forms (logical order kept)."""
    forms, ligs = _arabic_forms()
    types = [_joining(c, forms) for c in text]
    n, out, i = len(text), [], 0

    def prev_joins(i):
        j = i - 1
        while j >= 0 and types[j] == 'T':
            j -= 1
        return j >= 0 and types[j] in ('D', 'C')

    def next_index(i):
        k = i + 1
        while k < n and types[k] == 'T':
            k += 1
        return k

    while i < n:
        c, t = text[i], types[i]
        if t not in ('D', 'R'):
            out.append(c)
            i += 1
            continue
        k = next_index(i)
        pj = prev_joins(i)
        if c == 'ل' and k < n and (c, text[k]) in ligs:      # lam-alef ligature
            lig = ligs[(c, text[k])]
            out.append(lig.get('final' if pj else 'isolated') or lig.get('isolated'))
            out.extend(text[i + 1:k])                               # marks between lam and alef
            i = k + 1
            continue
        nj = t == 'D' and k < n and types[k] in ('D', 'R', 'C')
        f = forms[c]
        form = 'medial' if pj and nj else 'final' if pj else 'initial' if nj else 'isolated'
        out.append(f.get(form) or f.get('isolated') or c)
        i += 1
    return ''.join(out)


# ------------------------------------------------------------------ fonts and measuring
@lru_cache(maxsize=64)
def _cmap(path):
    p, idx = split_index(path)
    try:
        from fontTools.ttLib import TTFont
        return frozenset((TTFont(p, fontNumber=idx, lazy=True).getBestCmap() or {}).keys())
    except Exception:
        return None


def missing_glyphs(path, text):
    """Characters of `text` the font cannot draw (PowerPoint would substitute another font for them)."""
    chars = sorted({c for c in text if unicodedata.category(c)[0] not in 'CZ'})
    cmap = _cmap(path)
    if cmap is not None:
        return [c for c in chars if ord(c) not in cmap]
    p, idx = split_index(path)
    font = ImageFont.truetype(p, 48, index=idx)
    notdef = (font.getbbox('\U000F0000'), font.getlength('\U000F0000'))
    return [c for c in chars if unicodedata.category(c)[0] != 'M'
            and (font.getbbox(c), font.getlength(c)) == notdef]


def raqm_available():
    if os.environ.get('UNSCREENSHOT_NO_RAQM') == '1':
        return False
    try:
        from PIL import features
        return bool(features.check('raqm'))
    except Exception:
        return False


def paragraph_rtl(text, direction=None, lang=None):
    """Direction of a paragraph: the spec's "dir" if given, else its letters' (majority), else the language's
    (a line of digits and signs in an Arabic slide is a right-to-left paragraph)."""
    if direction:
        return direction == 'rtl'
    if any(unicodedata.bidirectional(c) in ('L', 'R', 'AL') for c in text):
        return profile(text)['rtl']
    return LANG_FAMILY.get((lang or 'en').split('-')[0].lower()) in ('arabic', 'hebrew')


def visual(text, rtl):
    """Display order of one line in a paragraph of direction `rtl`: a simplified Unicode bidi algorithm (rules
    W1-W7, N1-N2, I1-I2, L2) on letter clusters. Numbers stay left-to-right inside right-to-left text, the
    percent sign after Arabic-Indic digits goes to their left, Latin words keep their order."""
    clusters = []
    for ch in text:
        if clusters and unicodedata.category(ch) in ('Mn', 'Me'):
            clusters[-1] += ch
        else:
            clusters.append(ch)
    n = len(clusters)
    if not n:
        return text
    sos = 'R' if rtl else 'L'
    t = [unicodedata.bidirectional(c[0]) or 'ON' for c in clusters]
    last = sos
    for i in range(n):                       # W1-W3
        if t[i] == 'NSM':
            t[i] = t[i - 1] if i else sos
        if t[i] in ('L', 'R', 'AL'):
            last = t[i]
        elif t[i] == 'EN' and last == 'AL':
            t[i] = 'AN'
    t = ['R' if x == 'AL' else x for x in t]
    for i in range(1, n - 1):                # W4
        if t[i] == 'ES' and t[i - 1] == t[i + 1] == 'EN':
            t[i] = 'EN'
        elif t[i] == 'CS' and t[i - 1] == t[i + 1] and t[i - 1] in ('EN', 'AN'):
            t[i] = t[i - 1]
    i = 0
    while i < n:                             # W5
        if t[i] == 'ET':
            j = i
            while j < n and t[j] == 'ET':
                j += 1
            if (i and t[i - 1] == 'EN') or (j < n and t[j] == 'EN'):
                t[i:j] = ['EN'] * (j - i)
            i = j
        else:
            i += 1
    t = ['ON' if x in ('ES', 'ET', 'CS') else x for x in t]  # W6
    last = sos
    for i in range(n):                       # W7
        if t[i] in ('L', 'R'):
            last = t[i]
        elif t[i] == 'EN' and last == 'L':
            t[i] = 'L'

    def strong(x):
        return 'L' if x == 'L' else 'R' if x in ('R', 'EN', 'AN') else None
    i = 0
    while i < n:                             # N1-N2
        if strong(t[i]) is None:
            j = i
            while j < n and strong(t[j]) is None:
                j += 1
            before = strong(t[i - 1]) if i else sos
            after = strong(t[j]) if j < n else sos
            t[i:j] = [before if before == after else sos] * (j - i)
            i = j
        else:
            i += 1
    lv = [(0 if x == 'L' else 1 if x == 'R' else 2) if not rtl else (1 if x == 'R' else 2) for x in t]  # I1-I2
    for level in range(max(lv), 0, -1):     # L2
        i = 0
        while i < n:
            if lv[i] >= level:
                j = i
                while j < n and lv[j] >= level:
                    j += 1
                clusters[i:j], lv[i:j] = clusters[i:j][::-1], lv[i:j][::-1]
                i = j
            else:
                i += 1
    return ''.join(clusters)


def _visual(text):
    return visual(text, True)


def _prepare(path, text, size, lang, prof, rtl=None):
    """Font and drawing arguments for `text` in a paragraph of direction `rtl` (default: the text's own):
    (font, text to draw, kwargs, method, width_ok)."""
    rtl = prof['rtl'] if rtl is None else rtl
    p, idx = split_index(path)
    if raqm_available():
        font = ImageFont.truetype(p, size, index=idx, layout_engine=ImageFont.Layout.RAQM)
        kw = {'direction': 'rtl' if rtl else 'ltr'}
        if lang:
            kw['language'] = lang.split('-')[0]
        return font, text, kw, 'raqm', True
    font = ImageFont.truetype(p, size, index=idx, layout_engine=ImageFont.Layout.BASIC)
    shown, method, ok = text, 'basic', True
    if prof['family'] == 'arabic':
        shaped = arabic_shape(text)
        if shaped != text and not missing_glyphs(path, shaped):
            shown, method = shaped, 'arabic-joiner'
        elif shaped != text:
            ok = False
    elif prof['family'] in NEEDS_SHAPING or prof['script'] in NEEDS_SHAPING_SCRIPTS:
        ok = False
    shown = visual(shown, rtl)  # display order: what PowerPoint draws from left to right
    return font, shown, {}, method if ok else 'unshaped', ok


def ink_extents(font, text, **kw):
    """Ink box (x0, top, x1, bottom) of `text` drawn at the font's size, relative to the left end of its
    baseline. Pillow's getbbox() is the layout box horizontally (it starts at the origin and runs to the
    advance), so the ink is read from the drawn text: side bearings, spaces and the blank halves of full-width
    punctuation are not ink."""
    import numpy as np
    from PIL import Image, ImageDraw
    x0, top, x1, bottom = font.getbbox(text, anchor='ls', **kw)
    pad = int(font.size * 0.3) + 4
    w, h = int(x1 - x0) + 2 * pad, int(bottom - top) + 2 * pad
    img = Image.new('L', (max(1, w), max(1, h)), 0)
    ox, oy = pad - x0, pad - top
    ImageDraw.Draw(img).text((ox, oy), text, fill=255, font=font, anchor='ls', **kw)
    a = np.asarray(img) > 64
    cols, rows = np.flatnonzero(a.any(axis=0)), np.flatnonzero(a.any(axis=1))
    if not len(cols):
        return 0.0, 0.0, 0.0, 0.0
    return (float(cols[0] - ox), float(rows[0] - oy), float(cols[-1] + 1 - ox), float(rows[-1] + 1 - oy))


def measure(path, text, size, lang=None, prof=None, rtl=None):
    """Ink box of `text` drawn at `size` px, relative to the left end of its baseline (y up is negative).

    Returns {x0, top, x1, bottom, advance, method, width_ok}. `width_ok` is False when the width cannot be
    trusted (complex script without a shaping engine): fit on the ink height instead.
    """
    prof = prof or profile(text)
    font, shown, kw, method, ok = _prepare(path, text, size, lang, prof, rtl)
    x0, top, x1, bottom = ink_extents(font, shown, **kw)
    res = {'x0': x0, 'top': top, 'x1': x1, 'bottom': bottom, 'advance': font.getlength(shown, **kw),
           'method': method, 'width_ok': ok}
    if not ok and prof['family'] == 'arabic':
        w = arabic_width(path, text, size)  # the font's own contextual forms, read with fontTools
        if w:
            k = w[0] / max(1e-6, res['x1'] - res['x0'])
            res.update({'x0': w[1], 'x1': w[1] + w[0], 'advance': w[2], 'method': 'arabic-gsub', 'width_ok': True})
            res['scale'] = round(k, 3)
    return res


def bands(path, text, size, lang=None, prof=None, rtl=None):
    """Row profile of `text` drawn in the font, with the same rules analyze.py applies to the image: bottom of
    the densest band (analyze's "baseline") and the core band (rows >= 30 % of the densest), relative to the
    real baseline (positive = below). Shaping does not move these bands (a Devanagari headline stays put)."""
    import numpy as np
    from PIL import Image, ImageDraw
    prof = prof or profile(text)
    font, shown, kw, method, _ = _prepare(path, text, size, lang, prof, rtl)
    x0, top, x1, bottom = font.getbbox(shown, anchor='ls', **kw)
    pad = int(size * 0.3) + 4  # ink can overhang the layout box
    img = Image.new('L', (int(x1 - x0) + 2 * pad, int(bottom - top) + 2 * pad), 0)
    ImageDraw.Draw(img).text((pad - x0, pad - top), shown, fill=255, font=font, anchor='ls', **kw)
    rows = (np.asarray(img) > 50).sum(axis=1).astype(float)
    if not rows.max():
        return None
    dense = np.flatnonzero(rows >= 0.5 * rows.max())
    core = np.flatnonzero(rows >= 0.3 * rows.max())
    base = pad - top
    out = {'method': method, 'dense_top': float(dense[0] - base), 'dense_bottom': float(dense[-1] + 1 - base),
           'core_top': float(core[0] - base), 'core_bottom': float(core[-1] + 1 - base)}
    hl = headline_metrics(rows)
    if hl:
        out['headline_top'], out['body_bottom'] = hl[0] - base, hl[1] - base
    return out


# ------------------------------------------------------------------ Arabic widths from the font's own forms
@lru_cache(maxsize=16)
def _gsub_forms(path):
    """cmap, advances, glyph x-extents and the init/medi/fina/isol + lam-alef substitutions of an OpenType
    Arabic font (fontTools). None when fontTools or the tables are missing."""
    p, idx = split_index(path)
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(p, fontNumber=idx, lazy=True)
        cmap, hmtx, upm = f.getBestCmap(), f['hmtx'].metrics, f['head'].unitsPerEm
        gsub = f['GSUB'].table if 'GSUB' in f else None
        glyf = f['glyf'] if 'glyf' in f else None
    except Exception:
        return None
    if gsub is None or not gsub.FeatureList:
        return None
    subs = {t: {} for t in ('isol', 'init', 'medi', 'fina')}
    ligs = {}
    for rec in gsub.FeatureList.FeatureRecord:
        tag = rec.FeatureTag
        if tag not in subs and tag not in ('rlig', 'liga'):
            continue
        for li in rec.Feature.LookupListIndex:
            lk = gsub.LookupList.Lookup[li]
            for st in lk.SubTable:
                kind = lk.LookupType
                if kind == 7:
                    st, kind = st.ExtSubTable, st.ExtensionLookupType
                if kind == 1 and tag in subs:
                    for a, b in st.mapping.items():
                        subs[tag].setdefault(a, b)
                elif kind == 4 and tag in ('rlig', 'liga'):
                    for first, seq in st.ligatures.items():
                        for lig in seq:
                            ligs.setdefault((first,) + tuple(lig.Component), lig.LigGlyph)

    def extent(g):
        if glyf is not None:
            try:
                gl = glyf[g]
                if hasattr(gl, 'xMin'):
                    return gl.xMin, gl.xMax
            except Exception:
                pass
        adv = hmtx.get(g, (0, 0))
        return adv[1], adv[0] - adv[1] if adv[0] else adv[1]
    return cmap, hmtx, upm, subs, ligs, extent


def arabic_width(path, text, size):
    """(ink width, left bearing, advance) in px of Arabic-script `text`, joined with the font's own
    contextual forms and lam-alef ligatures (no kerning). None if the font cannot be read."""
    data = _gsub_forms(path)
    if not data:
        return None
    cmap, hmtx, upm, subs, ligs, extent = data
    forms, _ = _arabic_forms()
    types = [_joining(c, forms) for c in text]
    n = len(text)
    glyphs = []
    for i, c in enumerate(text):
        g = cmap.get(ord(c))
        if g is None:
            return None
        t = types[i]
        if t in ('D', 'R'):
            j = i - 1
            while j >= 0 and types[j] == 'T':
                j -= 1
            k = i + 1
            while k < n and types[k] == 'T':
                k += 1
            pj = j >= 0 and types[j] in ('D', 'C')
            nj = t == 'D' and k < n and types[k] in ('D', 'R', 'C')
            form = 'medi' if pj and nj else 'fina' if pj else 'init' if nj else 'isol'
            g = subs[form].get(g, g)
        if t == 'T':
            continue  # marks do not advance
        if glyphs and (glyphs[-1], g) in ligs:
            glyphs[-1] = ligs[(glyphs[-1], g)]
            continue
        glyphs.append(g)
    if not glyphs:
        return None
    adv = sum(hmtx.get(g, (0, 0))[0] for g in glyphs)
    vis = glyphs[::-1]  # right to left: the last logical glyph is drawn leftmost
    left = extent(vis[0])[0]
    right = adv - hmtx.get(vis[-1], (0, 0))[0] + extent(vis[-1])[1]
    k = size / upm
    return (right - left) * k, left * k, adv * k
