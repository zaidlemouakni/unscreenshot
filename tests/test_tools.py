"""prepare.py, probe.py, crop.py, env_check.py and the packaging script."""
import os
import re
import tempfile
import unittest
import zipfile

from PIL import Image

from helpers import DEMO, ROOT, run

SRC = os.path.join(DEMO, 'source.png')


class PrepareTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_transparent_png_is_flattened_on_white(self):
        src = os.path.join(self.d, 'in.png')
        Image.new('RGBA', (1600, 900), (255, 0, 0, 0)).save(src)
        log = run('prepare.py', src, '--out', os.path.join(self.d, 'work'))
        img = Image.open(os.path.join(self.d, 'work', 'source.png'))
        self.assertEqual((img.mode, img.size, img.getpixel((5, 5))), ('RGB', (1600, 900), (255, 255, 255)))
        self.assertIn('1600x900', log)

    def test_small_jpeg_is_flagged(self):
        src = os.path.join(self.d, 'in.jpg')
        Image.new('RGB', (800, 450), (10, 20, 30)).save(src, quality=95)
        self.assertIn('low resolution', run('prepare.py', src, '--out', os.path.join(self.d, 'work')))

    def test_pdf_pages(self):
        try:
            import fitz  # noqa: F401
        except ImportError:
            try:
                import pypdfium2  # noqa: F401
            except ImportError:
                from common import which
                if not which('pdftoppm'):
                    self.skipTest('no PDF rasteriser (PyMuPDF, pypdfium2 or pdftoppm)')
        pdf = os.path.join(self.d, 'deck.pdf')
        pages = [Image.new('RGB', (960, 540), c).convert('P') for c in ((250, 0, 0), (0, 0, 250), (0, 160, 0))]
        pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=72)
        log = run('prepare.py', pdf, '--out', os.path.join(self.d, 'work'), '--pages', '1,3', '--dpi', '144')
        files = re.findall(r'^(\S.*?\.png)\s', log, re.M)
        self.assertEqual(len(files), 2, log)
        colours = [Image.open(f).convert('RGB').getpixel((50, 50)) for f in files]
        self.assertGreater(colours[0][0], 200)  # page 1 red
        self.assertGreater(colours[1][1], 120)  # page 3 green


class ProbeCropTest(unittest.TestCase):
    def test_probe_modes(self):
        self.assertRegex(run('probe.py', SRC, 'color', 1500, 400), r'^#1B2340')  # the dark risks panel
        box = run('probe.py', SRC, 'box', 1500, 700)
        self.assertIn('box [1336,', box)
        ink = run('probe.py', SRC, 'ink', 90, 1005, 700, 1040)  # the footer line
        self.assertIn('baseline 1029', ink)
        self.assertIn('->', run('probe.py', SRC, 'h', 991, 0, 400))
        self.assertIn('->', run('probe.py', SRC, 'v', 1500, 300, 800))

    def test_crop_writes_a_zoomed_grid(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, 'crop.png')
            run('crop.py', SRC, 90, 120, 400, 180, '--zoom', 3, '--out', out)
            with Image.open(out) as im:
                w, h = im.size
            self.assertGreaterEqual(w, 310 * 3)
            self.assertGreaterEqual(h, 60 * 3)


class EnvAndPackageTest(unittest.TestCase):
    def test_env_check(self):
        log = run('env_check.py')
        self.assertIn('Metric-exact fonts here', log)
        self.assertNotIn('BLOCKING', log)

    def test_package(self):
        with tempfile.TemporaryDirectory() as d:
            run(os.path.join(ROOT, 'scripts', 'package_skill.py'), '--out', d)
            with zipfile.ZipFile(os.path.join(d, 'unscreenshot.zip')) as z:
                names = z.namelist()
                self.assertIn('unscreenshot/SKILL.md', names)
                self.assertIn('unscreenshot/LICENSE.txt', names)
                self.assertIn('unscreenshot/scripts/build_pptx.py', names)
                self.assertIn('unscreenshot/reference/spec-format.md', names)
                self.assertTrue(all(n.startswith('unscreenshot/') for n in names))
                self.assertFalse([n for n in names if '__pycache__' in n or n.endswith('.pyc')])
                skill_md = z.read('unscreenshot/SKILL.md')
            with zipfile.ZipFile(os.path.join(d, 'unscreenshot-flat.zip')) as z:
                self.assertEqual(z.read('SKILL.md'), skill_md)
                self.assertEqual(len(z.namelist()), len(names))
            self.assertLess(os.path.getsize(os.path.join(d, 'unscreenshot.zip')), 1024 * 1024)
            # reproducible: a second build gives the same bytes
            with open(os.path.join(d, 'unscreenshot.zip'), 'rb') as f:
                first = f.read()
            run(os.path.join(ROOT, 'scripts', 'package_skill.py'), '--out', d)
            with open(os.path.join(d, 'unscreenshot.zip'), 'rb') as f:
                self.assertEqual(f.read(), first)


if __name__ == '__main__':
    unittest.main()
