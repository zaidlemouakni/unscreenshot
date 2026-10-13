"""The whole rebuild in two commands; the model only reads the text in between.

    python scripts/run.py start <image or pdf> --out DIR
        prepares and analyses each page, writes DIR/p01/read_*.png (every text line, enlarged, with its id) and
        DIR/p01/texts.txt (one `T7: ` line per text line, to fill in)
    python scripts/run.py finish --out DIR [--pptx slide.pptx]
        reads the texts, writes the spec (draft.py), fits, builds, renders and corrects (up to 3 rounds), and
        lists the lines whose reading does not match the image (crops in DIR/p01/reread/) - fix them in
        texts.txt and run finish again.

Options of finish: --rounds N (correction rounds, default 3), --keep-spec (use DIR/pNN/spec.json as it is: a spec
edited by hand), --pptx PATH (the deck to write, default DIR/slides.pptx).
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import find_font_file, load_json, ui_font  # noqa: E402
from textshape import profile, raqm_available  # noqa: E402

HEADER = """# Read every line in read_*.png (same folder) and write its exact text after its id, in reading order:
# case, accents, punctuation, symbols and digits exactly as shown (١٢٪, ۱۲٪ and 12% are different texts).
# Right-to-left text: type it as it is read, not as it is displayed. Do not translate or correct anything.
# Leave the text empty when the line is not text (part of a logo or a drawing).
"""


def call(script, *args, quiet=False):
    r = subprocess.run([sys.executable, os.path.join(HERE, script), *map(str, args)], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    if r.returncode:
        sys.exit(f'{script} failed:\n{r.stdout[-2500:]}\n{r.stderr[-2500:]}')
    if not quiet and r.stdout.strip():
        print(r.stdout.rstrip())
    return r.stdout


def pages(out):
    return sorted(p for p in glob.glob(os.path.join(out, 'p[0-9][0-9]')) if os.path.isdir(p))


# ------------------------------------------------------------------ start
def reading_sheets(page_dir, an, lines):
    src = Image.open(an['image']).convert('RGB')
    W, H = src.size
    font = ui_font(22)
    rows, files, used, no = [], [], 0, 1

    def flush():
        nonlocal rows, used, no
        if rows:
            w = max(r.width for r in rows)
            sheet = Image.new('RGB', (w, sum(r.height for r in rows)), (255, 255, 255))
            y = 0
            for r in rows:
                sheet.paste(r, (0, y))
                y += r.height
            p = os.path.join(page_dir, f'read_{no}.png')
            sheet.save(p)
            files.append(p)
            rows, used, no = [], 0, no + 1

    for ln in lines:
        x0, y0, x1, y1 = ln['box']
        crop = src.crop((max(0, x0 - 6), max(0, y0 - 6), min(W, x1 + 6), min(H, y1 + 6)))
        k = max(1.0, min(5.0, 64.0 / max(1, crop.height)))
        crop = crop.resize((max(1, round(crop.width * k)), max(1, round(crop.height * k))), Image.LANCZOS)
        if crop.width > 2200:
            crop = crop.resize((2200, max(1, round(crop.height * 2200 / crop.width))), Image.LANCZOS)
        row = Image.new('RGB', (crop.width + 110, crop.height + 14), (255, 255, 255))
        d = ImageDraw.Draw(row)
        d.text((6, 7), ln['id'], fill=(210, 0, 0), font=font)
        d.line([(0, row.height - 1), (row.width, row.height - 1)], fill=(220, 220, 220))
        row.paste(crop, (104, 7))
        if used + row.height > 1500:
            flush()
        rows.append(row)
        used += row.height
    flush()
    return files


def start(a):
    import draft
    out = a.out
    os.makedirs(out, exist_ok=True)
    for old in pages(out) + [os.path.join(out, 'input')]:  # a previous run in the same folder
        shutil.rmtree(old, ignore_errors=True)
    tmp = os.path.join(out, 'input')
    call('prepare.py', a.input, '--out', tmp, quiet=True)
    sources = sorted(glob.glob(os.path.join(tmp, 'source*.png')))
    if not sources:
        sys.exit('prepare.py produced no image')
    print(f'{len(sources)} slide(s)')
    for n, src in enumerate(sources, 1):
        page = os.path.join(out, f'p{n:02d}')
        os.makedirs(page, exist_ok=True)
        shutil.copy(src, os.path.join(page, 'source.png'))
        call('analyze.py', os.path.join(page, 'source.png'), '--out', page, quiet=True)
        an = load_json(os.path.join(page, 'analysis.json'))
        lines, _ = draft.reading_lines(an)
        sheets = reading_sheets(page, an, lines)
        with open(os.path.join(page, 'texts.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(HEADER)
            for ln in lines:
                f.write(f"{ln['id']}: \n")
        print(f'p{n:02d}: {len(lines)} text lines -> read {", ".join(os.path.basename(s) for s in sheets)}, '
              f'fill {os.path.join(page, "texts.txt")}')
    print('\nNEXT: open each read_*.png, write every line\'s exact text after its id in texts.txt, then run:\n'
          f'  python {os.path.join(HERE, "run.py")} finish --out {out}')


# ------------------------------------------------------------------ finish
def check_texts(page, lines):
    import draft
    texts, problems = draft.parse_texts(os.path.join(page, 'texts.txt'))
    ids = [ln['id'] for ln in lines]
    missing = [i for i in ids if i not in texts]
    extra = [i for i in texts if i not in ids]
    if missing:
        problems.append(f'no line for {", ".join(missing[:12])}' + (' ...' if len(missing) > 12 else '')
                        + ' (write "T7: text", or "T7:" alone if it is not text)')
    if extra:
        problems.append(f'unknown ids {", ".join(extra[:12])} (use the ids shown in read_*.png)')
    if ids and not any(texts.get(i, '').strip() for i in ids):
        problems.append('every text is empty: read the lines in read_*.png first')
    return texts, problems


def verify_reading(page, spec_fitted, an):
    """Lines whose text does not fill the width it has in the image: a word missed, added or misread.
    Each line's text is drawn in the chosen font at the line's own cap height; its width ratio to the image is
    compared with the median ratio of the lines in the same font (which cancels the difference between the
    source font and its Office substitute). Writes enlarged crops to reread/ and returns [(id, ratio, text)]."""
    import fontmatch
    idx = {t['id']: t for t in an['texts']}
    rows = []
    for el in spec_fitted['elements']:
        if el['type'] not in ('text', 'bullets') or (el.get('fit') or {}).get('mode') == 'spacing':
            continue
        refs = el.get('from') or []
        refs = refs if isinstance(refs, list) else [refs]
        src_lines = el.get('lines') or [t for it in el.get('items', []) for t in (it if isinstance(it, list) else [it])]
        font_key = (el.get('font', 'Arial'), bool(el.get('bold')))
        path = find_font_file(font_key[0], bold=font_key[1])[0]
        if not path or len(refs) != len(src_lines):
            continue
        for ref, ln, box in zip(refs, src_lines, el.get('line_boxes') or []):
            text = ln if isinstance(ln, str) else ''.join(r['text'] for r in ln)
            first = idx.get(str(ref).split('+')[0])
            if not first or len(text.strip()) < 4:
                continue
            fam = profile(text)['family']
            if fam in ('indic', 'sea') and not raqm_available():
                continue  # widths of unshaped Devanagari or Thai say nothing about the reading
            cap = first['baseline'] - first.get('cap_top', first['box'][1])
            if fam == 'alphabetic' and not any(ch.isupper() or ch.isdigit() for ch in text):
                # no capital to measure (the top of a "t" is not a cap height): size from the x-height
                cap = (first['baseline'] - first.get('x_top', first['box'][1])) / fontmatch._font_metrics(path)[1]
            c = fontmatch.candidate_features(path, text, cap, fam if fam in ('alphabetic', 'arabic') else 'alphabetic')
            if c and c['w'] > 0:
                rows.append((str(ref).split('+')[0], (box[2] - box[0]) / c['w'], text, box, font_key, fam))
    flagged = []
    all_ratios = [r[1] for r in rows]
    for lid, ratio, text, box, font_key, fam in rows:
        same = [r[1] for r in rows if r[4] == font_key]
        ref_ratio = sorted(same)[len(same) // 2] if len(same) >= 3 else sorted(all_ratios)[len(all_ratios) // 2]
        rel = ratio / ref_ratio
        lo, hi = (0.82, 1.22) if fam == 'alphabetic' else (0.75, 1.33)
        if not lo <= rel <= hi:
            flagged.append((lid, rel, text, box))
    rd = os.path.join(page, 'reread')
    shutil.rmtree(rd, ignore_errors=True)
    if flagged:
        os.makedirs(rd, exist_ok=True)
        src = Image.open(an['image']).convert('RGB')
        for lid, _, _, box in flagged:
            x0, y0, x1, y1 = box
            crop = src.crop((max(0, x0 - 8), max(0, y0 - 8), x1 + 8, y1 + 8))
            k = max(2.0, min(6.0, 90.0 / max(1, crop.height)))
            crop.resize((round(crop.width * k), round(crop.height * k)), Image.LANCZOS).save(os.path.join(rd, f'{lid}.png'))
    return [(lid, rel, text) for lid, rel, text, _ in flagged]


def renderer_available():
    from common import powerpoint_available, which
    return bool(which('soffice', 'libreoffice') or powerpoint_available())


def finish(a):
    import draft
    out = a.out
    pps = pages(out)
    if not pps:
        sys.exit(f'nothing in {out}: run "run.py start <image> --out {out}" first')
    all_problems = {}
    for page in pps:
        an = load_json(os.path.join(page, 'analysis.json'))
        lines, _ = draft.reading_lines(an)
        texts, problems = check_texts(page, lines)
        if problems:
            all_problems[page] = problems
    if all_problems:
        for page, problems in all_problems.items():
            for p in problems:
                print(f'{os.path.basename(page)}/texts.txt: {p}')
        sys.exit('Fix texts.txt, then run finish again.')
    fitted = []
    for page in pps:
        spec = os.path.join(page, 'spec.json')
        if not (a.keep_spec and os.path.exists(spec)):
            call('draft.py', os.path.join(page, 'analysis.json'), os.path.join(page, 'texts.txt'), '--out', spec, quiet=True)
        call('fit.py', spec, '--out', os.path.join(page, 'spec.fitted.json'), quiet=True)
        fitted.append(os.path.join(page, 'spec.fitted.json'))
    pptx = os.path.abspath(a.pptx or os.path.join(out, 'slides.pptx'))
    call('build_pptx.py', *fitted, '--out', pptx, quiet=True)
    checked = renderer_available()
    rounds_done = 0
    if checked:
        best = None
        current = list(fitted)
        for rnd in range(1, a.rounds + 1):
            mads, todo = [], False
            for n, (page, spec) in enumerate(zip(pps, current), 1):
                chk = os.path.join(page, f'check{rnd}')
                log = call('check.py', pptx, spec, '--out', chk, '--slide', n, quiet=True)
                m = re.search(r'mean luminance difference: ([\d.]+)', open(os.path.join(chk, 'report.txt'), encoding='utf-8').read())
                mads.append(float(m.group(1)) if m else 99.0)
                if 'No correction needed' not in log and os.path.exists(os.path.join(chk, 'spec.corrected.json')):
                    todo = True
            rounds_done = rnd
            score = sum(mads) / len(mads)
            if best is None or score < best[0]:
                best = (score, list(current), rnd)
                shutil.copy(pptx, pptx + '.best')
            if not todo or rnd == a.rounds:
                break
            current = [os.path.join(page, f'check{rnd}', 'spec.corrected.json') for page in pps]
            call('build_pptx.py', *current, '--out', pptx, quiet=True)
        if best and os.path.exists(pptx + '.best'):
            shutil.move(pptx + '.best', pptx)
            for page, spec in zip(pps, best[1]):
                shutil.copy(os.path.join(page, f'check{best[2]}', 'side_by_side.png'), os.path.join(page, 'side_by_side.png'))
    # report
    print(f'DONE: {pptx}' + (f'  ({rounds_done} check round(s), mean difference {best[0]:.1f}/255)' if checked and best else
                              '  (no renderer here: not checked visually)'))
    to_reread = []
    for page, spec in zip(pps, fitted):
        sp = load_json(spec)
        an = load_json(os.path.join(page, 'analysis.json'))
        fonts, approx = set(), set()
        for el in sp['elements']:
            if el['type'] in ('text', 'bullets'):
                fonts.add(el.get('font', 'Arial') + (' Bold' if el.get('bold') else ''))
                if not (el.get('fitted') or {}).get('exact', True):
                    approx.add(el.get('font', 'Arial'))
        pics = sum(1 for el in sp['elements'] if el['type'] == 'image')
        side = os.path.join(page, 'side_by_side.png')
        print(f'{os.path.basename(page)}: fonts {", ".join(sorted(fonts))}'
              + (f' (not installed here, sizes estimated: {", ".join(sorted(approx))})' if approx else '')
              + f'; {pics} picture(s) kept from the image' + (f'; compare: {side}' if os.path.exists(side) else ''))
        for lid, ratio, text in verify_reading(page, sp, an):
            to_reread.append((page, lid, ratio, text))
    if to_reread:
        print('\nRE-READ these lines (their text does not fill the width they have in the image):')
        for page, lid, ratio, text in to_reread:
            hint = 'text too short: a word or characters missing?' if ratio > 1 else 'text too long: extra or wrong characters?'
            print(f'  {os.path.basename(page)} {lid}: "{text}"  ({hint})  -> {os.path.join(page, "reread", lid + ".png")}')
        print('Fix them in texts.txt and run finish again (at most twice); otherwise deliver as it is.')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('start')
    s.add_argument('input')
    s.add_argument('--out', default='unscreenshot_work')
    f = sub.add_parser('finish')
    f.add_argument('--out', default='unscreenshot_work')
    f.add_argument('--pptx')
    f.add_argument('--rounds', type=int, default=3)
    f.add_argument('--keep-spec', action='store_true')
    a = ap.parse_args()
    (start if a.cmd == 'start' else finish)(a)


if __name__ == '__main__':
    main()
