"""Minimal PowerPoint (.pptx) writer using only the Python standard library.

Covers what slide reconstruction needs: slide size and background, preset shapes (rect, roundRect,
ellipse, homePlate, chevron...) with adjustments, custom polygons, straight connectors with dashes and
arrowheads, text boxes with exact line spacing, bullets, mixed-style runs and letter-spacing, pictures,
and groups. Everything is native and editable in PowerPoint, Keynote, Google Slides and LibreOffice.
"""
import datetime
import zipfile
from xml.sax.saxutils import escape

NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
REL_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
R_SLIDE = REL_NS + '/slide'
R_LAYOUT = REL_NS + '/slideLayout'
R_MASTER = REL_NS + '/slideMaster'
R_THEME = REL_NS + '/theme'
R_IMAGE = REL_NS + '/image'
EMU_PT = 12700

_CTRL = {c: None for c in range(32) if c not in (9, 10, 13)}


def esc(s, attr=False):
    s = str(s).translate(_CTRL)
    return escape(s, {'"': '&quot;'} if attr else {})


def hexc(color):
    return str(color).strip().lstrip('#').upper()[:6]


def fill_xml(color, alpha=None):
    if color in (None, '', 'none'):
        return '<a:noFill/>'
    a = f'<a:alpha val="{int(round(alpha * 100000))}"/>' if alpha is not None and alpha < 1 else ''
    return f'<a:solidFill><a:srgbClr val="{hexc(color)}">{a}</a:srgbClr></a:solidFill>'


DASHES = {'solid': None, 'dash': 'dash', 'dot': 'sysDot', 'sysdot': 'sysDot', 'dashdot': 'dashDot',
          'longdash': 'lgDash', 'rounddot': 'sysDot'}


def line_xml(line):
    """line: None (no outline) or {'color', 'width_emu', 'dash', 'head', 'tail'}."""
    if not line:
        return '<a:ln><a:noFill/></a:ln>'
    dash = DASHES.get(line.get('dash') or 'solid')
    d = f'<a:prstDash val="{dash}"/>' if dash else ''
    head = '<a:headEnd type="triangle"/>' if line.get('head') else ''
    tail = '<a:tailEnd type="triangle"/>' if line.get('tail') else ''
    return (f'<a:ln w="{int(line.get("width_emu", EMU_PT))}" cap="flat">{fill_xml(line.get("color", "#000000"))}'
            f'{d}{head}{tail}</a:ln>')


def xfrm(x, y, cx, cy, rot=0, flip_h=False, flip_v=False):
    attrs = ''
    if rot:
        attrs += f' rot="{int(round(rot * 60000))}"'
    if flip_h:
        attrs += ' flipH="1"'
    if flip_v:
        attrs += ' flipV="1"'
    return f'<a:xfrm{attrs}><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{max(0, int(cx))}" cy="{max(0, int(cy))}"/></a:xfrm>'


# ------------------------------------------------------------------ text
def run_xml(text, st, lang):
    """st: font (Latin slot), font_ea (CJK), font_cs (Arabic, Hebrew, Thai, Indic...), lang, size_pt, bold,
    italic, underline, color, spacing_pt. PowerPoint picks the slot per character."""
    lang = st.get('lang') or lang
    attrs = f' lang="{esc(lang, True)}" sz="{int(round(st["size_pt"] * 100))}"'
    if st.get('bold'):
        attrs += ' b="1"'
    if st.get('italic'):
        attrs += ' i="1"'
    if st.get('underline'):
        attrs += ' u="sng"'
    if st.get('spacing_pt'):
        attrs += f' spc="{int(round(st["spacing_pt"] * 100))}"'
    font = st.get('font', 'Arial')
    latin, ea, cs = (esc(f, True) for f in (font, st.get('font_ea') or font, st.get('font_cs') or font))
    rpr = (f'<a:rPr{attrs} dirty="0">{fill_xml(st.get("color", "#000000"))}'
           f'<a:latin typeface="{latin}"/><a:ea typeface="{ea}"/><a:cs typeface="{cs}"/></a:rPr>')
    return f'<a:r>{rpr}<a:t>{esc(text)}</a:t></a:r>'


def br_xml(st, lang):
    return f'<a:br><a:rPr lang="{lang}" sz="{int(round(st["size_pt"] * 100))}" dirty="0"/></a:br>'


def paragraph_xml(lines, base, para, lang):
    """lines: list of lines, each a list of (text, style) runs. para: align, line_pt, before_pt, bullet, rtl.

    `align` is what the eye sees, also in right-to-left paragraphs (measured: algn stays visual with rtl="1");
    a right-to-left bulleted paragraph must be right-aligned for its bullet to sit on the right."""
    algn = {'left': 'l', 'center': 'ctr', 'right': 'r', 'justify': 'just'}.get(para.get('align', 'left'), 'l')
    ppr_attrs = f' algn="{algn}"' + (' rtl="1"' if para.get('rtl') else '')
    bul = para.get('bullet')
    if bul:
        ppr_attrs += f' marL="{int(bul["mar_emu"])}" indent="{-int(bul["mar_emu"])}"'
    inner = ''
    if para.get('line_pt'):
        inner += f'<a:lnSpc><a:spcPts val="{int(round(para["line_pt"] * 100))}"/></a:lnSpc>'
    if para.get('before_pt'):
        inner += f'<a:spcBef><a:spcPts val="{int(round(para["before_pt"] * 100))}"/></a:spcBef>'
    if bul:
        inner += (f'<a:buClr><a:srgbClr val="{hexc(bul["color"])}"/></a:buClr>'
                  f'<a:buSzPct val="{int(bul.get("size_pct", 100) * 1000)}"/>'
                  f'<a:buFont typeface="{esc(bul.get("font", "Arial"), True)}"/>'
                  f'<a:buChar char="{esc(bul.get("char", "•"), True)}"/>')
    else:
        inner += '<a:buNone/>'
    body = ''
    for i, runs in enumerate(lines):
        if i:
            body += br_xml(base, lang)
        for text, st in runs:
            if text:
                body += run_xml(text, st, lang)
    end = f'<a:endParaRPr lang="{lang}" sz="{int(round(base["size_pt"] * 100))}" dirty="0"/>'
    return f'<a:p><a:pPr{ppr_attrs}>{inner}</a:pPr>{body}{end}</a:p>'


def body_xml(paragraphs, wrap=False, anchor='t', ins=(0, 0, 0, 0)):
    l, t, r, b = (int(v) for v in ins)
    return (f'<p:txBody><a:bodyPr wrap="{"square" if wrap else "none"}" lIns="{l}" tIns="{t}" rIns="{r}" '
            f'bIns="{b}" anchor="{anchor}" rtlCol="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
            f'{"".join(paragraphs)}</p:txBody>')


# ------------------------------------------------------------------ slide content
class _Group:
    def __init__(self, gid, name):
        self.id, self.name, self.items = gid, name, []
        self.box = None

    def grow(self, x, y, cx, cy):
        b = (x, y, x + cx, y + cy)
        self.box = b if self.box is None else (min(self.box[0], b[0]), min(self.box[1], b[1]),
                                               max(self.box[2], b[2]), max(self.box[3], b[3]))

    def xml(self):
        x0, y0, x1, y1 = self.box or (0, 0, 0, 0)
        tr = (f'<a:xfrm><a:off x="{x0}" y="{y0}"/><a:ext cx="{x1 - x0}" cy="{y1 - y0}"/>'
              f'<a:chOff x="{x0}" y="{y0}"/><a:chExt cx="{x1 - x0}" cy="{y1 - y0}"/></a:xfrm>')
        return (f'<p:grpSp><p:nvGrpSpPr><p:cNvPr id="{self.id}" name="{esc(self.name, True)}"/><p:cNvGrpSpPr/>'
                f'<p:nvPr/></p:nvGrpSpPr><p:grpSpPr>{tr}</p:grpSpPr>{"".join(self.items)}</p:grpSp>')


class Slide:
    def __init__(self, deck, number):
        self.deck, self.number = deck, number
        self.items = []          # top-level XML strings or _Group objects, in paint order
        self.groups = {}
        self.images = []         # (rId, media name)
        self.background = None
        self._id = 1

    def _next(self):
        self._id += 1
        return self._id

    def _place(self, xml, group, box):
        if group:
            g = self.groups.get(group)
            if g is None:
                g = self.groups[group] = _Group(self._next(), group)
                self.items.append(g)
            g.items.append(xml)
            g.grow(*box)
        else:
            self.items.append(xml)

    def shape(self, name, x, y, cx, cy, prst='rect', adj=None, fill=None, alpha=None, line=None, rot=0,
              text=None, group=None, textbox=False, flip_h=False, flip_v=False):
        """Preset shape. adj: list of fractions (0..1) for the preset's adjust handles. text: txBody XML.
        flip_h mirrors the geometry (a chevron pointing left), not the text."""
        sid = self._next()
        av = ''.join(f'<a:gd name="{"adj" if i == 0 and len(adj) == 1 else f"adj{i + 1}"}" '
                     f'fmla="val {int(round(v * 100000))}"/>' for i, v in enumerate(adj or []))
        nv = f'<p:cNvSpPr txBox="1"/>' if textbox else '<p:cNvSpPr/>'
        xml = (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{esc(name, True)}"/>{nv}<p:nvPr/></p:nvSpPr>'
               f'<p:spPr>{xfrm(x, y, cx, cy, rot, flip_h, flip_v)}<a:prstGeom prst="{prst}"><a:avLst>{av}</a:avLst></a:prstGeom>'
               f'{fill_xml(fill, alpha)}{line_xml(line)}</p:spPr>{text or ""}</p:sp>')
        self._place(xml, group, (int(x), int(y), int(cx), int(cy)))

    def polygon(self, name, points, fill=None, alpha=None, line=None, group=None):
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        x0, y0 = min(xs), min(ys)
        w, h = max(1, max(xs) - x0), max(1, max(ys) - y0)
        path = f'<a:moveTo><a:pt x="{int(points[0][0] - x0)}" y="{int(points[0][1] - y0)}"/></a:moveTo>'
        path += ''.join(f'<a:lnTo><a:pt x="{int(px - x0)}" y="{int(py - y0)}"/></a:lnTo>' for px, py in points[1:])
        geom = (f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
                f'<a:pathLst><a:path w="{int(w)}" h="{int(h)}">{path}<a:close/></a:path></a:pathLst></a:custGeom>')
        sid = self._next()
        xml = (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{esc(name, True)}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
               f'<p:spPr>{xfrm(x0, y0, w, h)}{geom}{fill_xml(fill, alpha)}{line_xml(line)}</p:spPr></p:sp>')
        self._place(xml, group, (int(x0), int(y0), int(w), int(h)))

    def connector(self, name, x1, y1, x2, y2, line, group=None):
        sid = self._next()
        x, y = min(x1, x2), min(y1, y2)
        cx, cy = abs(x2 - x1), abs(y2 - y1)
        xml = (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{sid}" name="{esc(name, True)}"/><p:cNvCxnSpPr/><p:nvPr/>'
               f'</p:nvCxnSpPr><p:spPr>{xfrm(x, y, cx, cy, 0, x2 < x1, y2 < y1)}'
               f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom>{line_xml(line)}</p:spPr></p:cxnSp>')
        self._place(xml, group, (int(x), int(y), int(cx), int(cy)))

    def picture(self, name, png_bytes, x, y, cx, cy, descr='', group=None):
        sid = self._next()
        rid = f'rId{len(self.images) + 2}'
        media = self.deck.add_media(png_bytes)
        self.images.append((rid, media))
        xml = (f'<p:pic><p:nvPicPr><p:cNvPr id="{sid}" name="{esc(name, True)}" descr="{esc(descr, True)}"/>'
               f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
               f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
               f'<p:spPr>{xfrm(x, y, cx, cy)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
        self._place(xml, group, (int(x), int(y), int(cx), int(cy)))

    def xml(self):
        bg = ''
        if self.background:
            bg = f'<p:bg><p:bgPr>{fill_xml(self.background)}<a:effectLst/></p:bgPr></p:bg>'
        shapes = ''.join(i.xml() if isinstance(i, _Group) else i for i in self.items)
        tree = ('<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm>'
                '<a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm>'
                '</p:grpSpPr>')
        return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:sld {NS}><p:cSld>{bg}<p:spTree>{tree}'
                f'{shapes}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')

    def rels(self):
        r = [f'<Relationship Id="rId1" Type="{R_LAYOUT}" Target="../slideLayouts/slideLayout1.xml"/>']
        r += [f'<Relationship Id="{rid}" Type="{R_IMAGE}" Target="../media/{m}"/>' for rid, m in self.images]
        return _rels(r)


def _rels(items):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{"".join(items)}'
            '</Relationships>')


THEME = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme"><a:themeElements>'
    '<a:clrScheme name="Office"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>'
    '<a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="44546A"/></a:dk2>'
    '<a:lt2><a:srgbClr val="E7E6E6"/></a:lt2><a:accent1><a:srgbClr val="4472C4"/></a:accent1>'
    '<a:accent2><a:srgbClr val="ED7D31"/></a:accent2><a:accent3><a:srgbClr val="A5A5A5"/></a:accent3>'
    '<a:accent4><a:srgbClr val="FFC000"/></a:accent4><a:accent5><a:srgbClr val="5B9BD5"/></a:accent5>'
    '<a:accent6><a:srgbClr val="70AD47"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink>'
    '<a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme>'
    '<a:fontScheme name="Office"><a:majorFont><a:latin typeface="Calibri Light"/><a:ea typeface=""/><a:cs typeface=""/>'
    '</a:majorFont><a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>'
    '</a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst>'
    + '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>' * 3 +
    '</a:fillStyleLst><a:lnStyleLst>'
    + ''.join(f'<a:ln w="{w}"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>' for w in (6350, 12700, 19050)) +
    '</a:lnStyleLst><a:effectStyleLst>' + '<a:effectStyle><a:effectLst/></a:effectStyle>' * 3 +
    '</a:effectStyleLst><a:bgFillStyleLst>' + '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>' * 3 +
    '</a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>')

_EMPTY_TREE = ('<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr>'
               '<a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>'
               '</a:xfrm></p:grpSpPr></p:spTree>')
MASTER = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:sldMaster {NS}><p:cSld><p:bg><p:bgRef idx="1001">'
          f'<a:schemeClr val="bg1"/></p:bgRef></p:bg>{_EMPTY_TREE}</p:cSld>'
          '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" '
          'accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
          '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles>'
          '<p:titleStyle><a:lvl1pPr><a:defRPr sz="4400"/></a:lvl1pPr></p:titleStyle>'
          '<p:bodyStyle><a:lvl1pPr><a:defRPr sz="1800"/></a:lvl1pPr></p:bodyStyle>'
          '<p:otherStyle><a:lvl1pPr><a:defRPr sz="1800"/></a:lvl1pPr></p:otherStyle></p:txStyles></p:sldMaster>')
LAYOUT = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:sldLayout {NS} type="blank" preserve="1">'
          f'<p:cSld name="Blank">{_EMPTY_TREE}</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')


class Deck:
    def __init__(self, width_emu, height_emu, title='Slide', creator='unscreenshot'):
        self.w, self.h = int(width_emu), int(height_emu)
        self.slides, self.media = [], []
        self.title, self.creator = title, creator

    def add_slide(self):
        s = Slide(self, len(self.slides) + 1)
        self.slides.append(s)
        return s

    def add_media(self, png_bytes):
        name = f'image{len(self.media) + 1}.png'
        self.media.append((name, png_bytes))
        return name

    def save(self, path):
        n = len(self.slides)
        ct = ['<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
              '<Default Extension="xml" ContentType="application/xml"/>',
              '<Default Extension="png" ContentType="image/png"/>',
              '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
              '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
              '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
              '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
              '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>',
              '<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>',
              '<Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>',
              '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
              '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>']
        ct += [f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
               for i in range(1, n + 1)]
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        pres_rels = [f'<Relationship Id="rId1" Type="{R_MASTER}" Target="slideMasters/slideMaster1.xml"/>']
        pres_rels += [f'<Relationship Id="rId{i + 1}" Type="{R_SLIDE}" Target="slides/slide{i}.xml"/>' for i in range(1, n + 1)]
        pres_rels += [f'<Relationship Id="rId{n + 2}" Type="{R_THEME}" Target="theme/theme1.xml"/>',
                      f'<Relationship Id="rId{n + 3}" Type="{REL_NS}/presProps" Target="presProps.xml"/>',
                      f'<Relationship Id="rId{n + 4}" Type="{REL_NS}/viewProps" Target="viewProps.xml"/>',
                      f'<Relationship Id="rId{n + 5}" Type="{REL_NS}/tableStyles" Target="tableStyles.xml"/>']
        sld_ids = ''.join(f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, n + 1))
        presentation = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:presentation {NS} saveSubsetFonts="1">'
                        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
                        f'<p:sldIdLst>{sld_ids}</p:sldIdLst><p:sldSz cx="{self.w}" cy="{self.h}"/>'
                        '<p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/>'
                        '</a:defPPr></p:defaultTextStyle></p:presentation>')
        files = {
            '[Content_Types].xml': ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns='
                                    f'"http://schemas.openxmlformats.org/package/2006/content-types">{"".join(ct)}</Types>'),
            '_rels/.rels': _rels([
                f'<Relationship Id="rId1" Type="{REL_NS}/officeDocument" Target="ppt/presentation.xml"/>',
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>',
                f'<Relationship Id="rId3" Type="{REL_NS}/extended-properties" Target="docProps/app.xml"/>']),
            'docProps/core.xml': ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<cp:coreProperties '
                                  'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                                  'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
                                  'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                  f'<dc:title>{esc(self.title)}</dc:title><dc:creator>{esc(self.creator)}</dc:creator>'
                                  f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
                                  f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>'),
            'docProps/app.xml': ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Properties xmlns='
                                 '"http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
                                 f'<Application>unscreenshot</Application><Slides>{n}</Slides></Properties>'),
            'ppt/presentation.xml': presentation,
            'ppt/_rels/presentation.xml.rels': _rels(pres_rels),
            'ppt/slideMasters/slideMaster1.xml': MASTER,
            'ppt/slideMasters/_rels/slideMaster1.xml.rels': _rels([
                f'<Relationship Id="rId1" Type="{R_LAYOUT}" Target="../slideLayouts/slideLayout1.xml"/>',
                f'<Relationship Id="rId2" Type="{R_THEME}" Target="../theme/theme1.xml"/>']),
            'ppt/slideLayouts/slideLayout1.xml': LAYOUT,
            'ppt/slideLayouts/_rels/slideLayout1.xml.rels': _rels([
                f'<Relationship Id="rId1" Type="{R_MASTER}" Target="../slideMasters/slideMaster1.xml"/>']),
            'ppt/theme/theme1.xml': THEME,
            'ppt/presProps.xml': f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:presentationPr {NS}/>',
            'ppt/viewProps.xml': f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:viewPr {NS}/>',
            'ppt/tableStyles.xml': ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<a:tblStyleLst xmlns:a='
                                    '"http://schemas.openxmlformats.org/drawingml/2006/main" '
                                    'def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>'),
        }
        for s in self.slides:
            files[f'ppt/slides/slide{s.number}.xml'] = s.xml()
            files[f'ppt/slides/_rels/slide{s.number}.xml.rels'] = s.rels()
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('[Content_Types].xml', files.pop('[Content_Types].xml'))
            for name, data in files.items():
                z.writestr(name, data)
            for name, data in self.media:
                z.writestr(f'ppt/media/{name}', data)
