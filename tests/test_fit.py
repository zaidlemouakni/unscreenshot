"""fit.py: "from" references and font-size fitting."""
import unittest

import helpers  # noqa: F401 (puts the scripts on sys.path)
import fit
from common import find_font_file, load_font

ANALYSIS = {
    'texts': [
        {'id': 'T1', 'box': [100, 50, 400, 80], 'baseline': 75, 'cap_top': 55, 'x_top': 60, 'color': '#111111'},
        {'id': 'T2', 'box': [100, 90, 350, 120], 'baseline': 115, 'cap_top': 95, 'x_top': 100, 'color': '#111111'},
    ],
    'regions': [{'id': 'R1', 'box': [10, 10, 210, 110], 'color': '#FFFFFF', 'shape': 'pill'},
                {'id': 'R2', 'box': [0, 0, 50, 50], 'color': '#EEEEEE', 'shape': 'roundrect', 'radius': 6}],
    'rules': [{'id': 'L1', 'box': [0, 200, 500, 202], 'color': '#CCCCCC'},
              {'id': 'L2', 'box': [300, 10, 301, 90], 'color': '#CCCCCC'}],
    'graphics': [{'id': 'G1', 'box': [20, 20, 60, 60]}],
    'marks': [],
}


class ResolveTest(unittest.TestCase):
    def setUp(self):
        self.idx = fit.index_analysis(ANALYSIS)

    def resolved(self, el):
        fit.resolve(el, self.idx)
        return el

    def test_text_block(self):
        el = self.resolved({'type': 'text', 'from': ['T1', 'T2']})
        self.assertEqual((el['x'], el['baseline'], el['pitch'], el['cap'], el['xh']), (100, 75, 40, 20, 15))
        self.assertEqual((el['line_w'], el['w'], el['color']), ([300, 250], 300, '#111111'))

    def test_alignment_sets_the_anchor(self):
        self.assertEqual(self.resolved({'type': 'text', 'from': ['T1', 'T2'], 'align': 'right'})['x'], 400)
        self.assertEqual(self.resolved({'type': 'text', 'from': ['T1', 'T2'], 'align': 'center'})['x'], 250)

    def test_explicit_values_win(self):
        el = self.resolved({'type': 'text', 'from': 'T1', 'x': 99, 'color': '#FF0000'})
        self.assertEqual((el['x'], el['color'], el['baseline']), (99, '#FF0000', 75))

    def test_bullets(self):
        el = self.resolved({'type': 'bullets', 'from': ['T1', 'T2'], 'x': 80})
        self.assertEqual((el['text_x'], el['x'], el['pitch']), (100, 80, 40))

    def test_shapes_lines_images(self):
        self.assertEqual(self.resolved({'type': 'rect', 'from': 'R1'}),
                         {'type': 'rect', 'from': 'R1', 'box': [10, 10, 210, 110], 'fill': '#FFFFFF', 'radius': 'pill'})
        self.assertEqual(self.resolved({'type': 'rect', 'from': 'R2'})['radius'], 6)
        h = self.resolved({'type': 'line', 'from': 'L1'})
        self.assertEqual((h['p1'], h['p2'], h['width']), ([0, 201.0], [500, 201.0], 2))
        v = self.resolved({'type': 'line', 'from': 'L2'})
        self.assertEqual((v['p1'], v['p2'], v['width']), ([300.5, 10], [300.5, 90], 1))
        self.assertEqual(self.resolved({'type': 'image', 'from': 'G1'})['box'], [18, 18, 62, 62])
        self.assertEqual(self.resolved({'type': 'image', 'from': 'G1', 'pad': 0})['box'], [20, 20, 60, 60])

    def test_unknown_reference_is_reported_not_fatal(self):
        el = self.resolved({'type': 'text', 'from': 'T99', 'x': 1})
        self.assertEqual(el, {'type': 'text', 'from': 'T99', 'x': 1})


class FitTextTest(unittest.TestCase):
    SAMPLE = 'Quarterly revenue grew 12% in Europe'

    def setUp(self):
        path, exact, _ = find_font_file('Arial')
        if not (path and exact):
            self.skipTest('no Arial or metric-compatible twin (Liberation Sans, Arimo) installed')
        self.path = path
        self.font200 = load_font(path, fit.M)

    def ink_width(self, size):
        from textshape import ink_extents  # the drawn ink, not Pillow's layout box
        x0, _, x1, _ = ink_extents(load_font(self.path, size), self.SAMPLE)
        return x1 - x0

    def test_recovers_the_rendered_size(self):
        for size in (24, 48, 90):
            with self.subTest(size=size):
                el = fit.fit_text({'type': 'text', 'font': 'Arial', 'lines': [self.SAMPLE], 'w': self.ink_width(size)})
                self.assertTrue(el['fitted']['exact'])
                self.assertAlmostEqual(el['size'], size, delta=0.02 * size)
                self.assertGreaterEqual(el['lsb'], 0)

    def test_longest_line_drives_a_block(self):
        el = fit.fit_text({'type': 'text', 'font': 'Arial', 'lines': ['short', self.SAMPLE],
                           'line_w': [40, self.ink_width(48)]})
        self.assertAlmostEqual(el['size'], 48, delta=1)
        self.assertEqual(el['fitted']['sample'], self.SAMPLE)

    def test_spacing_mode_keeps_the_cap_height(self):
        w200, _ = fit.ink_metrics(self.font200, self.SAMPLE)
        hb = self.font200.getbbox('H')
        capr = (hb[3] - hb[1]) / fit.M
        target = w200 * 40 / fit.M + 2.0 * (len(self.SAMPLE) - 1)  # 40 px type tracked +2 px
        el = fit.fit_text({'type': 'text', 'font': 'Arial', 'lines': [self.SAMPLE], 'w': target,
                           'cap': capr * 40, 'fit': {'mode': 'spacing'}})
        self.assertAlmostEqual(el['size'], 40, places=1)
        self.assertAlmostEqual(el['spacing'], 2.0, places=2)

    def test_bullets_get_bullet_offset(self):
        el = fit.fit_text({'type': 'bullets', 'font': 'Arial', 'items': [self.SAMPLE, ['a', 'b']],
                           'w': self.ink_width(30), 'bullet': '●', 'bullet_size': 125})
        self.assertAlmostEqual(el['size'], 30, delta=0.6)
        self.assertIn('bullet_lsb', el)

    def test_unknown_font_falls_back_to_cap_height(self):
        el = fit.fit_text({'type': 'text', 'font': 'No Such Font 123', 'lines': ['Hello'], 'cap': 21})
        self.assertFalse(el['fitted']['exact'])
        self.assertAlmostEqual(el['size'], 30, delta=0.5)  # 21 px cap / 0.70 default cap ratio


if __name__ == '__main__':
    unittest.main()
