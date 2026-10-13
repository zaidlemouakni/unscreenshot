"""Normalise the user's input into RGB PNG files, one per slide.

    python scripts/prepare.py <image|pdf> [--out work] [--dpi 200] [--pages 1,3]

Images (png, jpg, webp, gif, bmp, tiff) are flattened on white. PDF pages are rasterised with PyMuPDF,
pypdfium2 or pdftoppm (whichever exists). Prints the produced files and their size.
"""
import argparse
import os
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import which  # noqa: E402


def to_png(img, path):
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA')
        bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img)
    img.convert('RGB').save(path)
    return path


def pdf_pages(pdf, out, dpi, pages):
    files = []
    try:
        import fitz  # PyMuPDF
        for i, page in enumerate(fitz.open(pdf), 1):
            if pages and i not in pages:
                continue
            p = os.path.join(out, f'source_p{i:02d}.png')
            page.get_pixmap(dpi=dpi).save(p)
            files.append(p)
        return files
    except ImportError:
        pass
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(pdf)
        for i in range(len(doc)):
            if pages and i + 1 not in pages:
                continue
            p = os.path.join(out, f'source_p{i + 1:02d}.png')
            to_png(doc[i].render(scale=dpi / 72).to_pil(), p)
            files.append(p)
        return files
    except ImportError:
        pass
    exe = which('pdftoppm')
    if not exe:
        sys.exit('Cannot rasterise the PDF (no PyMuPDF, pypdfium2 or pdftoppm). Ask for a PNG instead.')
    subprocess.run([exe, '-png', '-r', str(dpi), pdf, os.path.join(out, 'source_p')], check=True)
    for f in sorted(os.listdir(out)):
        if f.startswith('source_p') and f.endswith('.png'):
            n = int(f.rsplit('-', 1)[-1].split('.')[0]) if '-' in f else 1
            if not pages or n in pages:
                files.append(os.path.join(out, f))
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('--out', default='work')
    ap.add_argument('--dpi', type=int, default=200)
    ap.add_argument('--pages', default='')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pages = {int(x) for x in a.pages.split(',') if x.strip()}
    if a.input.lower().endswith('.pdf'):
        files = pdf_pages(a.input, a.out, a.dpi, pages)
    else:
        files = [to_png(Image.open(a.input), os.path.join(a.out, 'source.png'))]
    for f in files:
        w, h = Image.open(f).size
        note = '  (low resolution: measurements are coarser, prefer line centres)' if w < 1200 else ''
        print(f'{f}  {w}x{h}  ratio {w / h:.3f}{note}')


if __name__ == '__main__':
    main()
