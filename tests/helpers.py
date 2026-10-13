"""Shared paths and checks for the test suite (run with: python -m unittest discover -s tests -v)."""
import os
import posixpath
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, 'skills', 'unscreenshot')
SCRIPTS = os.path.join(SKILL, 'scripts')
DEMO = os.path.join(ROOT, 'examples', 'demo')
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'ct': 'http://schemas.openxmlformats.org/package/2006/content-types',
      'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}


def run(script, *args, cwd=None, timeout=600):
    """Run a skill script the way an agent does; return stdout, fail with its output."""
    path = script if os.path.isabs(script) else os.path.join(SCRIPTS, script)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, path] + [str(a) for a in args], capture_output=True, text=True,
                       encoding='utf-8', cwd=cwd, timeout=timeout, env=env)
    if r.returncode:
        raise AssertionError(f'{os.path.basename(path)} exited {r.returncode}\n{r.stdout}\n{r.stderr}')
    return r.stdout


def renderer():
    """'libreoffice', 'powerpoint' or None. UNSCREENSHOT_RENDER=0 disables rendering tests."""
    if os.environ.get('UNSCREENSHOT_RENDER') == '0':
        return None
    from common import powerpoint_available, which
    if which('soffice', 'libreoffice'):
        return 'libreoffice'
    if powerpoint_available():
        return 'powerpoint'
    return None


def validate_pptx(path):
    """Structural validation of a .pptx package. Returns {part name: parsed XML root} for the slides.

    Every XML part must be well-formed, every part must have a content type, every internal relationship
    must point at an existing part, slide shape ids must be unique, and the slide list must match the parts.
    """
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        for required in ('[Content_Types].xml', '_rels/.rels', 'ppt/presentation.xml',
                         'ppt/_rels/presentation.xml.rels'):
            assert required in names, f'missing part {required}'
        roots = {}
        for n in names:
            if n.endswith(('.xml', '.rels')):
                try:
                    roots[n] = ET.fromstring(z.read(n))
                except ET.ParseError as ex:
                    raise AssertionError(f'{n}: malformed XML ({ex})')
        ct = roots['[Content_Types].xml']
        defaults = {d.get('Extension').lower() for d in ct.findall('ct:Default', NS)}
        overrides = {o.get('PartName') for o in ct.findall('ct:Override', NS)}
        for n in names:
            if n == '[Content_Types].xml' or n.endswith('/'):
                continue
            ext = n.rsplit('.', 1)[-1].lower()
            assert '/' + n in overrides or ext in defaults, f'{n}: no content type'
        for o in overrides:
            assert o.lstrip('/') in names, f'content type override for a missing part {o}'
        for n in names:
            if not n.endswith('.rels'):
                continue
            folder = posixpath.dirname(posixpath.dirname(n))
            for rel in roots[n].findall('rel:Relationship', NS):
                if rel.get('TargetMode') == 'External':
                    continue
                target = rel.get('Target')
                full = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(folder, target))
                assert full in names, f'{n}: relationship {rel.get("Id")} points at a missing part {full}'
        slides = {n: r for n, r in roots.items() if n.startswith('ppt/slides/slide') and n.endswith('.xml')}
        pres = roots['ppt/presentation.xml']
        assert len(pres.findall('p:sldIdLst/p:sldId', NS)) == len(slides), 'slide list and slide parts differ'
        for n, r in slides.items():
            ids = [e.get('id') for e in r.iter(f'{{{NS["p"]}}}cNvPr')]
            assert len(ids) == len(set(ids)), f'{n}: duplicate shape ids'
        return slides


def shapes_by_name(slide_root):
    """{shape name: element} for sp, pic, cxnSp and grpSp elements of a slide."""
    out = {}
    for tag in ('sp', 'pic', 'cxnSp', 'grpSp'):
        for e in slide_root.iter(f'{{{NS["p"]}}}{tag}'):
            c = e.find('.//p:cNvPr', NS)
            out[c.get('name')] = e
    return out


def xfrm_of(shape):
    """(x, y, cx, cy) in EMU from a shape's own transform."""
    x = shape.find('./p:spPr/a:xfrm', NS)
    if x is None:
        x = shape.find('./p:grpSpPr/a:xfrm', NS)
    off, ext = x.find('a:off', NS), x.find('a:ext', NS)
    return int(off.get('x')), int(off.get('y')), int(ext.get('cx')), int(ext.get('cy'))
