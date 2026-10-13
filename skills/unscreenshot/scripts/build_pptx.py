"""Build an editable PowerPoint from one or more spec files (one slide per spec).

    python scripts/build_pptx.py work/spec.fitted.json [more specs...] --out out/slide.pptx

Spec coordinates are source-image pixels; the slide is 13.333 in wide and keeps the source ratio.
Everything is native and editable (text boxes, bullets, shapes, connectors) except "image" elements.
No third-party dependency besides Pillow and numpy (the .pptx is written by pptx_writer.py).

Text placement rule (measured in PowerPoint): with an exact line spacing P >= 1.25 x font size, the first
baseline sits 0.75 x P below the top of a zero-inset text box, for every font and size (Latin, CJK, Indic,
Thai, Arabic and Hebrew Office fonts; Dubai: 0.725). Single lines use P >= 1.25 x size; multi-line blocks
tighter than that are split into one grouped text box per line.

Every run gets its three font slots (Latin, East Asian, complex script) and its language; right-to-left
paragraphs are marked rtl and their bullets sit on the right; joined scripts are never letter-spaced.
"""
import argparse
import io
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SLIDE_W_EMU, SLIDE_W_PT, TIGHT_DESCENT, baseline_factor, load_json  # noqa: E402
from pptx_writer import Deck, body_xml, paragraph_xml  # noqa: E402
from textshape import guess_lang, measuring_font, paragraph_rtl, profile, slot_fonts  # noqa: E402


class Ctx:
    def __init__(self, slide, spec, src_img, outdir):
        self.slide = slide
        self.w, self.h = spec['size']
        self.k = SLIDE_W_EMU / float(self.w)     # EMU per source pixel
        self.kp = SLIDE_W_PT / float(self.w)     # points per source pixel
        self.src, self.outdir = src_img, outdir
        self.lang = spec.get('lang', 'en-US')
        self.notes = []

    def e(self, v):
        return int(round(v * self.k))

    def pt(self, v):
        return v * self.kp


def norm_lines(el):
    lines = el.get('lines')
    if lines is None:
        lines = [el.get('text', el.get('content', ''))]
    return [[{'text': ln}] if isinstance(ln, str) else ln for ln in lines]


def plain(lines):
    return ' '.join(''.join(r['text'] for r in ln) for ln in lines)


def is_rtl(el, text, ctx):
    return paragraph_rtl(text, el.get('dir'), el.get('lang') or ctx.lang)


def style(d, ctx, text=''):
    lang = d.get('lang') or guess_lang(text, ctx.lang)
    fonts = slot_fonts(d.get('font', 'Arial'), text, lang, d.get('font_ea'), d.get('font_cs'))
    spacing = 0 if profile(text)['joined'] else (d.get('spacing') or 0)  # spacing breaks joined scripts
    return {'font': fonts['latin'], 'font_ea': fonts['ea'], 'font_cs': fonts['cs'], 'lang': lang,
            'size_pt': ctx.pt(d['size']), 'bold': bool(d.get('bold')), 'italic': bool(d.get('italic')),
            'underline': bool(d.get('underline')), 'color': d.get('color', '#000000'),
            'spacing_pt': ctx.pt(spacing)}


KEYS = ('font', 'font_ea', 'font_cs', 'lang', 'size', 'bold', 'italic', 'color', 'spacing', 'underline')


def runs(line, el, ctx):
    base = {k: el[k] for k in KEYS if k in el}
    out = []
    for r in line:
        d = dict(base)
        d.update({k: v for k, v in r.items() if k != 'text'})
        out.append((r['text'], style(d, ctx, r['text'])))
    return out


def para(lines, el, ctx, P, **extra):
    text = plain(lines)
    p = {'align': el.get('align', 'left'), 'line_pt': ctx.pt(P), 'rtl': is_rtl(el, text, ctx)}
    p.update(extra)
    return paragraph_xml([runs(ln, el, ctx) for ln in lines], style(el, ctx, text), p, ctx.lang)


def est_width(el, lines):
    if el.get('width'):
        return el['width']
    chars = max(sum(len(r['text']) for r in ln) for ln in lines) if lines else 1
    return (el.get('w') or chars * 0.62 * el['size']) + el['size'] * 1.2


def text_box(ctx, name, left, top, width, height, paragraphs, group, wrap=False):
    ctx.slide.shape(name, ctx.e(left), ctx.e(top), ctx.e(width), ctx.e(height), prst='rect', fill=None, line=None,
                    text=body_xml(paragraphs, wrap=wrap), group=group, textbox=True)


def first_baseline(el, text, ctx):
    lang = el.get('lang') or guess_lang(text, ctx.lang)
    return baseline_factor(measuring_font(el.get('font', 'Arial'), text, lang, el.get('font_ea'), el.get('font_cs')))


def build_text(el, ctx):
    S = el['size']
    lines = norm_lines(el)
    n = len(lines)
    text = plain(lines)
    el = dict(el, align=el.get('align') or ('right' if is_rtl(el, text, ctx) else 'left'))
    pitch = el.get('pitch') or 1.3 * S
    align = el['align']
    spacing = 0 if profile(text)['joined'] else (el.get('spacing', 0) or 0)
    width = est_width(el, lines)
    lsb, rsb = el.get('lsb', 0.03 * S), el.get('rsb', 0.03 * S)
    if align == 'right':      # the box's right edge sits one right bearing (and trailing spacing) past the ink
        left = el['x'] + rsb + spacing - width
    elif align == 'center':   # the advance is centred in the box; the ink centre is offset by (lsb - rsb) / 2
        left = el['x'] + (rsb - lsb) / 2 + spacing / 2 - width / 2
    else:
        left = el['x'] - lsb
    base = el['baseline']
    f = first_baseline(el, text, ctx)
    name = el.get('id', 'text')
    if n == 1 or pitch >= 1.25 * S:
        P = max(pitch, 1.25 * S) if n == 1 else pitch
        text_box(ctx, name, left, base - f * P, width, P * n, [para(lines, el, ctx, P)], el.get('group'))
        return
    group = el.get('group') or name + '-lines'
    P = 1.3 * S
    for i, line in enumerate(lines):
        text_box(ctx, f'{name}-l{i + 1}', left, base + i * pitch - f * P, width, P, [para([line], el, ctx, P)], group)
    ctx.notes.append(f'{name}: line pitch {pitch:.1f}px < 1.25 x size -> one text box per line (grouped)')


def build_bullets(el, ctx):
    S = el['size']
    P = el.get('pitch') or 1.35 * S
    gap = el.get('gap', 0) or 0
    items = [it if isinstance(it, list) else [it] for it in el['items']]
    item_lines = [[[{'text': ln}] if isinstance(ln, str) else ln for ln in it] for it in items]
    text = ' '.join(plain(il) for il in item_lines)
    rtl = is_rtl(el, text, ctx)
    f = first_baseline(el, text, ctx)
    if P >= 1.25 * S:
        off = f * P
    else:
        off = max(f * P, P - TIGHT_DESCENT.get(el.get('font', '').lower(), 0.24) * S)
        ctx.notes.append(f"{el.get('id')}: tight line pitch ({P:.1f}px) -> approximate vertical placement, check it")
    nlines = sum(len(i) for i in items)
    chars = max(len(plain([ln])) for il in item_lines for ln in il)
    if rtl:  # mirrored: x is the bullet's right ink edge, text_x the text's right ink edge
        right = el['x'] + el.get('bullet_rsb', 0.06 * S)
        mar = right - el['text_x'] - el.get('rsb', 0.03 * S)
        width = el.get('width') or (mar + (el.get('w') or chars * 0.6 * S) + 1.2 * S)
        left = right - width
    else:
        left = el['x'] - el.get('bullet_lsb', 0.06 * S)
        mar = el['text_x'] - el.get('lsb', 0.03 * S) - left
        width = el.get('width') or (mar + (el.get('w') or chars * 0.6 * S) + 1.2 * S)
    bullet = {'mar_emu': ctx.e(mar), 'color': el.get('bullet_color', el.get('color', '#000000')),
              'size_pct': el.get('bullet_size', 100), 'font': el.get('bullet_font', 'Arial'),
              'char': el.get('bullet', '•')}
    paras = []
    for i, lines in enumerate(item_lines):
        extra = {'bullet': bullet, 'align': 'right' if rtl else 'left', 'rtl': rtl}
        if i and gap:
            extra['before_pt'] = ctx.pt(gap)
        paras.append(para(lines, el, ctx, P, **extra))
    text_box(ctx, el.get('id', 'bullets'), left, el['baseline'] - off, width, P * nlines + gap * (len(items) - 1),
             paras, el.get('group'), wrap=bool(el.get('wrap')))


def line_spec(line, ctx):
    if not line:
        return None
    return {'color': line.get('color', '#000000'), 'width_emu': ctx.e(line.get('width', 1)), 'dash': line.get('dash')}


def build_shape(el, ctx):
    x0, y0, x1, y1 = el['box']
    w, h = x1 - x0, y1 - y0
    m = max(1e-6, min(w, h))
    t = el['type']
    adj = None
    if t == 'ellipse':
        prst = 'ellipse'
    elif t == 'arrow':
        prst = 'chevron' if el.get('notch') else 'homePlate'
        adj = [max(0.0, min(w / m, el.get('tip', h / 2) / m))]
    else:
        r = el.get('radius', 0) or 0
        if r == 'pill' or r > 0:
            prst = 'roundRect'
            adj = [max(0.0, min(0.5, (m / 2 if r == 'pill' else r) / m))]
        else:
            prst = 'rect'
    text = None
    if el.get('text'):
        t_ = dict(el['text'])
        t_.setdefault('align', 'center')
        S = t_['size']
        P = max(t_.get('pitch') or 0, 1.25 * S)
        dy = t_.get('dy', 0) or 0
        pad = t_.get('pad', 0) or 0
        ins = (ctx.e(pad), ctx.e(2 * dy) if dy > 0 else 0, ctx.e(pad), ctx.e(-2 * dy) if dy < 0 else 0)
        text = body_xml([para(norm_lines(t_), t_, ctx, P)], wrap=False, anchor='ctr', ins=ins)
    flip = el.get('flip') or ''  # 'h': mirrored (a right-to-left roadmap's chevrons point left)
    ctx.slide.shape(el.get('id', t), ctx.e(x0), ctx.e(y0), ctx.e(w), ctx.e(h), prst=prst, adj=adj,
                    fill=el.get('fill'), alpha=el.get('opacity'), line=line_spec(el.get('line'), ctx),
                    rot=el.get('rotation', 0), text=text, group=el.get('group'), flip_h='h' in flip,
                    flip_v='v' in flip)


def build_polygon(el, ctx):
    ctx.slide.polygon(el.get('id', 'polygon'), [(ctx.e(x), ctx.e(y)) for x, y in el['points']], fill=el.get('fill'),
                      alpha=el.get('opacity'), line=line_spec(el.get('line'), ctx), group=el.get('group'))


def build_line(el, ctx):
    (x1, y1), (x2, y2) = el['p1'], el['p2']
    head = el.get('head', 'none')
    ln = {'color': el.get('color', '#000000'), 'width_emu': ctx.e(el.get('width', 1)), 'dash': el.get('dash'),
          'head': head in ('start', 'both'), 'tail': head in ('end', 'both')}
    ctx.slide.connector(el.get('id', 'line'), ctx.e(x1), ctx.e(y1), ctx.e(x2), ctx.e(y2), ln, group=el.get('group'))


def build_image(el, ctx):
    x0, y0, x1, y1 = el['box']
    if el.get('file'):
        img = Image.open(el['file']).convert('RGBA')
        up = el.get('upscale', 1)
    else:
        if ctx.src is None:
            raise ValueError('image element without "file" needs the spec "source" image')
        img = ctx.src.crop(tuple(int(round(v)) for v in (el.get('crop') or el['box']))).convert('RGBA')
        up = el.get('upscale', 3)
    key = el.get('transparent')
    if key:
        a = np.asarray(img).astype(np.int16)
        if key == 'auto':
            col = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])[:, :3], axis=0)
        else:
            k = key.lstrip('#')
            col = np.array([int(k[i:i + 2], 16) for i in (0, 2, 4)])
        d = np.abs(a[..., :3] - col).max(axis=2).astype(float)
        lo, hi = el.get('alpha_range', [10, 45])
        alpha = np.clip((d - lo) / max(1, hi - lo), 0, 1) * 255
        a[..., 3] = np.minimum(a[..., 3], alpha.astype(np.int16))
        img = Image.fromarray(a.astype(np.uint8), 'RGBA')
    if up and up != 1:
        img = img.resize((max(1, round(img.width * up)), max(1, round(img.height * up))), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    os.makedirs(os.path.join(ctx.outdir, 'assets'), exist_ok=True)
    img.save(os.path.join(ctx.outdir, 'assets', f"{el.get('id', 'img')}.png"))
    ctx.slide.picture(el.get('id', 'image'), buf.getvalue(), ctx.e(x0), ctx.e(y0), ctx.e(x1 - x0), ctx.e(y1 - y0),
                      descr=el.get('alt', ''), group=el.get('group'))


BUILDERS = {'text': build_text, 'bullets': build_bullets, 'rect': build_shape, 'ellipse': build_shape,
            'arrow': build_shape, 'polygon': build_polygon, 'line': build_line, 'image': build_image}


def resolve_source(spec, spec_path):
    p = spec.get('source')
    if not p:
        return None
    if not os.path.isabs(p):
        cand = os.path.join(os.path.dirname(os.path.abspath(spec_path)), p)
        p = cand if os.path.exists(cand) else p
    return Image.open(p).convert('RGB') if os.path.exists(p) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('specs', nargs='+')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    outdir = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(outdir, exist_ok=True)
    first = load_json(a.specs[0])
    w0, h0 = first['size']
    height = int(round(SLIDE_W_EMU * h0 / float(w0)))
    if abs(h0 / float(w0) - 9 / 16.0) < 0.01 * 9 / 16.0:
        height = 6858000  # snap to the standard 16:9 slide so it pastes cleanly into other decks
    deck = Deck(SLIDE_W_EMU, height, title=first.get('title', 'Slide'))
    for sp in a.specs:
        spec = load_json(sp)
        w, h = spec['size']
        if abs(w / float(h) - w0 / float(h0)) > 0.01:
            print(f'! {sp}: aspect ratio {w / h:.3f} differs from the first slide ({w0 / h0:.3f})')
        slide = deck.add_slide()
        slide.background = spec.get('background')
        ctx = Ctx(slide, spec, resolve_source(spec, sp), outdir)
        for el in spec['elements']:
            if el.get('skip'):
                continue
            try:
                BUILDERS[el['type']](el, ctx)
            except KeyError as ex:
                raise SystemExit(f"element {el.get('id')} ({el.get('type')}): missing field {ex} "
                                 "(run fit.py on the spec, or set it by hand)")
            except Exception as ex:
                raise SystemExit(f"element {el.get('id')} ({el.get('type')}): {ex}")
        for n in ctx.notes:
            print('  note:', n)
        print(f"slide {len(deck.slides)}: {len(spec['elements'])} elements from {os.path.basename(sp)}")
    deck.save(a.out)
    print('->', a.out)


if __name__ == '__main__':
    main()
