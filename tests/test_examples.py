"""End to end on every example slide: analyse -> fit -> build (-> render, correct once, compare when possible).

The specs reference analysis ids (T#, R#, M#...); if analyze.py starts numbering or measuring differently, the
positions below move and these tests say so. Sizes and non-Latin baselines are only checked where the fonts
used here have exact metrics and were measured (on other systems, or without fontTools for fonts that need it,
they are estimated), and x gets a few pixels of slack with a substitute font. UNSCREENSHOT_KEEP=<folder> keeps
outputs.
"""
import json
import os
import re
import shutil
import tempfile
import unittest

from helpers import NS, ROOT, renderer, run, shapes_by_name, validate_pptx

# (x, baseline, size in source px), validated by a PowerPoint render: every text within 1 px after one round
EXAMPLES = {
    'demo': {
        'texts': (28, 40), 'marks': 4, 'mad': 9.0,
        'expect': {'eyebrow': (97, 64, 18.06), 'title': (97, 159, 57.33), 'subtitle': (96, 274, 27.38),
                   'kpi1-value': (133, 430, 67.1), 'risks-list': (1380, 449, 22.34), 'q1-label': (187, 664, 22.4),
                   'footer': (97, 1029, 16.94)}},
    'languages': {
        'texts': (50, 50), 'marks': 0, 'mad': 6.0,
        'expect': {'title': (85, 101, 46.12), 'ar-heading': (473, 294, 30.16), 'fa-lines': (918, 356, 21.06),
                   'he-lines': (1361, 356, 21.06), 'zh-heading': (1446, 297.48, 30.16), 'ja-lines': (115, 632.5, 21.06),
                   'ko-heading': (559, 577.04, 30.16), 'hi-heading': (1001, 576.2, 30.16),
                   'th-lines': (1446, 634, 21.06), 'vi-heading': (115, 852, 30.16), 'ru-lines': (558, 910, 21.06),
                   'el-eyebrow': (1003, 800, 17.2)}},
    'arabic': {
        'texts': (30, 36), 'marks': 5, 'mad': 5.0,
        'expect': {'title': (1824, 147, 53.87), 'subtitle': (1822, 281.74, 25.94), 'kpi1-value': (1790, 423, 59.93),
                   'kpi2-label': (1375, 479.8, 19.83), 'risks-list': (540, 463.89, 21.1),
                   'q1-label': (1674, 675.09, 22.32), 'q4-text': (957, 742.91, 18.94), 'footer': (1823, 1026.92, 15.98)}},
    'japanese': {
        'texts': (34, 42), 'marks': 6, 'mad': 4.0,
        'expect': {'eyebrow': (99, 64.44, 19.57), 'title': (98, 152.75, 52.03), 'subtitle': (100, 281.55, 24.97),
                   'kpi2-value': (544, 428.36, 60.16), 'kpi1-label': (133, 477.83, 19.17),
                   'risks-list': (1380, 461.61, 20.03), 'q2-text': (395, 741.98, 18.13), 'footer': (98, 1027.08, 14.69)}},
}


from fit import MEASURED  # noqa: E402 (helpers put the scripts on sys.path)

ALPHABETIC = ('LATIN', 'CYRILLIC', 'GREEK')


def spec_words(el):
    src = el.get('lines') or el.get('items') or (el.get('text') or {}).get('lines') or []
    for line in src:
        for part in (line if isinstance(line, list) else [line]):
            text = part if isinstance(part, str) else part.get('text', '')
            if text.strip():
                yield text.strip()


class ExampleBase:
    NAME = None

    @classmethod
    def setUpClass(cls):
        keep = os.environ.get('UNSCREENSHOT_KEEP')
        cls.tmp = None
        if keep:
            cls.dir = os.path.join(keep, cls.NAME)
            shutil.rmtree(cls.dir, ignore_errors=True)
            os.makedirs(cls.dir)
        else:
            cls.tmp = tempfile.TemporaryDirectory()
            cls.dir = cls.tmp.name
        d, ex = cls.dir, os.path.join(ROOT, 'examples', cls.NAME)
        cls.conf = EXAMPLES[cls.NAME]
        run('analyze.py', os.path.join(ex, 'source.png'), '--out', os.path.join(d, 'work'))
        with open(os.path.join(d, 'work', 'analysis.json'), encoding='utf-8') as f:
            cls.analysis = json.load(f)
        with open(os.path.join(ex, 'spec.json'), encoding='utf-8') as f:
            spec = json.load(f)
        cls.spec = json.loads(json.dumps(spec))
        spec['source'] = os.path.join(ex, 'source.png')
        spec['analysis'] = os.path.join(d, 'work', 'analysis.json')
        with open(os.path.join(d, 'spec.json'), 'w', encoding='utf-8') as f:
            json.dump(spec, f, ensure_ascii=False)
        run('fit.py', os.path.join(d, 'spec.json'), '--out', os.path.join(d, 'spec.fitted.json'))
        with open(os.path.join(d, 'spec.fitted.json'), encoding='utf-8') as f:
            cls.fitted = {e['id']: e for e in json.load(f)['elements']}
        cls.pptx = os.path.join(d, 'out', f'{cls.NAME}.pptx')
        run('build_pptx.py', os.path.join(d, 'spec.fitted.json'), '--out', cls.pptx)
        cls.slide = validate_pptx(cls.pptx)['ppt/slides/slide1.xml']
        cls.shapes = shapes_by_name(cls.slide)

    @classmethod
    def tearDownClass(cls):
        if cls.tmp:
            cls.tmp.cleanup()

    def test_analysis_finds_the_layout(self):
        a = self.analysis
        lo, hi = self.conf['texts']
        self.assertEqual((a['width'], a['height']), (1920, 1080))
        self.assertTrue(lo <= len(a['texts']) <= hi, len(a['texts']))
        self.assertEqual(len(a['marks']), self.conf['marks'])
        ids = {e['id'] for k in ('texts', 'regions', 'rules', 'graphics', 'marks') for e in a[k]}
        for el in self.spec['elements']:
            refs = el.get('from') or []
            for ref in refs if isinstance(refs, list) else [refs]:
                for r in ref.split('+'):
                    self.assertIn(r, ids, f"{el['id']} references {r}, missing from the analysis")

    def test_positions_and_sizes(self):
        for name, (x, base, size) in self.conf['expect'].items():
            el = self.fitted[name]
            f = el['fitted']
            # exact: the font PowerPoint will use is installed here and the fit measured on it
            exact = f['exact'] and bool(f.get('method'))
            with self.subTest(element=name):
                # x depends on the side bearings of the font actually used: a substitute moves it a little
                self.assertLessEqual(abs(el['x'] - x), 2 if exact else 6, f"x {el['x']} != {x}")
                # the analysis baseline is the real one for alphabetic scripts; the others are corrected on the
                # font's own glyphs (CJK ink box, Indic headline, Arabic letter bodies)
                if exact or (el.get('baseline_from') == 'analysis' and f.get('script') in ALPHABETIC):
                    self.assertLessEqual(abs(el['baseline'] - base), 2, f"baseline {el['baseline']} != {base}")
                # sizes solved from measured ink; 'body height' and 'height' are estimates (an unshaped font)
                if exact and f.get('method') in MEASURED:
                    self.assertAlmostEqual(el['size'], size, delta=0.04 * size)

    def test_roles_share_one_size(self):
        roles = {}
        for el in self.fitted.values():
            if el.get('role'):
                roles.setdefault(el['role'], set()).add(el['size'])
        for role, sizes in roles.items():
            self.assertEqual(len(sizes), 1, f'role {role} has several sizes {sizes}')

    def test_pptx_holds_every_word(self):
        text = ' '.join(t.text or '' for t in self.slide.iter(f'{{{NS["a"]}}}t'))
        for el in self.spec['elements']:
            for words in spec_words(el):
                with self.subTest(text=words):
                    self.assertIn(words, text)

    def test_round_trip(self):
        r = renderer()
        if not r:
            self.skipTest('no renderer (LibreOffice or PowerPoint), or UNSCREENSHOT_RENDER=0')
        d = self.dir
        run('check.py', self.pptx, os.path.join(d, 'spec.fitted.json'), '--out', os.path.join(d, 'check1'))
        pptx2 = os.path.join(d, 'out', f'{self.NAME}_round2.pptx')
        run('build_pptx.py', os.path.join(d, 'check1', 'spec.corrected.json'), '--out', pptx2)
        run('check.py', pptx2, os.path.join(d, 'check1', 'spec.corrected.json'), '--out', os.path.join(d, 'check2'))
        with open(os.path.join(d, 'check2', 'report.txt'), encoding='utf-8') as f:
            report = f.read()
        print(f'\n--- {self.NAME}: round trip with {r}, after one correction round ---\n{report}')
        mad = float(re.search(r'mean luminance difference: ([\d.]+)', report).group(1))
        # a blank slide scores ~30; LibreOffice substitutes fonts on most systems, so only PowerPoint is held tight
        self.assertLess(mad, self.conf['mad'] if r == 'powerpoint' else 20.0)
        if r == 'powerpoint':
            rows = re.findall(r'^(\S+)\s+dx\s+([+-][\d.]+)\s+dy\s+([+-][\d.]+)\s+width x([\d.]+)', report, re.M)
            self.assertGreater(len(rows), 10)
            for name, dx, dy, wr in rows:
                with self.subTest(element=name):
                    self.assertLessEqual(abs(float(dx)), 2.5)
                    self.assertLessEqual(abs(float(dy)), 2.5)
                    self.assertAlmostEqual(float(wr), 1.0, delta=0.08)


def runs_of(shape):
    return [(r.find('a:rPr', NS), r.find('a:t', NS).text) for r in shape.iter(f'{{{NS["a"]}}}r')]


class TestDemo(ExampleBase, unittest.TestCase):
    NAME = 'demo'


class TestLanguages(ExampleBase, unittest.TestCase):
    NAME = 'languages'

    def test_language_and_font_slots(self):
        want = {'ar': ('ar-SA', 'cs', 'Dubai'), 'fa': ('fa-IR', 'cs', 'Segoe UI'), 'he': ('he-IL', 'cs', 'Segoe UI'),
                'zh': ('zh-CN', 'ea', 'Microsoft YaHei'), 'ja': ('ja-JP', 'ea', 'Yu Gothic'),
                'ko': ('ko-KR', 'ea', 'Malgun Gothic'), 'hi': ('hi-IN', 'cs', 'Nirmala UI'),
                'th': ('th-TH', 'cs', 'Leelawadee UI'), 'vi': ('vi-VN', 'latin', 'Arial'),
                'ru': ('ru-RU', 'latin', 'Calibri'), 'el': ('el-GR', 'latin', 'Segoe UI'),
                'es': ('es-ES', 'latin', 'Segoe UI')}
        for code, (lang, slot, font) in want.items():
            with self.subTest(card=code):
                rpr, _ = runs_of(self.shapes[f'{code}-heading'])[0]
                self.assertEqual(rpr.get('lang'), lang)
                self.assertEqual(rpr.find(f'a:{slot}', NS).get('typeface'), font)
                ppr = self.shapes[f'{code}-heading'].find('.//a:pPr', NS)
                self.assertEqual(ppr.get('rtl') == '1', code in ('ar', 'fa', 'he'))
        # browsers put the percent sign left of Persian digits; PowerPoint does too for an en-US run
        number = [rpr.get('lang') for rpr, t in runs_of(self.shapes['fa-lines']) if t == '۱۲٪']
        self.assertEqual(number, ['en-US'])


class TestArabic(ExampleBase, unittest.TestCase):
    NAME = 'arabic'

    def test_right_to_left_layout(self):
        for name in ('title', 'subtitle', 'kpi1-value', 'q1-text', 'footer'):
            with self.subTest(element=name):
                # a text whose line pitch is tight is built as one box per line: '<id>-l1', '<id>-l2'...
                ppr = (self.shapes.get(name) or self.shapes[f'{name}-l1']).find('.//a:pPr', NS)
                self.assertEqual((ppr.get('rtl'), ppr.get('algn')), ('1', 'r'))
        bullets = self.shapes['risks-list'].findall('.//a:pPr', NS)
        self.assertEqual({(p.get('rtl'), p.get('algn')) for p in bullets}, {('1', 'r')})
        for q in ('q1', 'q2', 'q3', 'q4'):  # the roadmap points left
            self.assertEqual(self.shapes[f'{q}-bar'].find('p:spPr/a:xfrm', NS).get('flipH'), '1')
        self.assertIsNone(self.shapes['page-number'].find('.//a:pPr', NS).get('rtl'))


class TestJapanese(ExampleBase, unittest.TestCase):
    NAME = 'japanese'

    def test_east_asian_font_and_language(self):
        rprs = [rpr for rpr, _ in runs_of(self.shapes['subtitle'])]
        self.assertTrue(all(r.find('a:ea', NS).get('typeface') == 'Yu Gothic' for r in rprs))
        self.assertEqual({r.get('lang') for r in rprs}, {'ja-JP'})
        if self.fitted['eyebrow']['fitted']['exact']:  # spacing is only fitted with the real font
            eyebrow = runs_of(self.shapes['eyebrow'])
            self.assertTrue(all(r.get('spc') for r, _ in eyebrow), 'letter-spacing kept for CJK')


if __name__ == '__main__':
    unittest.main()
