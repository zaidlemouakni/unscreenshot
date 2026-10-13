"""The scripts alone rebuild every example slide: analysis -> reading lines -> texts -> draft.py -> fit.py ->
build_pptx.py. The texts are the true ones, taken from the hand-made spec, so no model is involved: this is what
the skill produces with any model once the text is read. The built deck must hold the same text and the same
objects (text lines, rectangles, chevrons, bullets, lines, pictures) as the hand-made reference."""
import json
import os
import sys
import tempfile
import unittest

from helpers import ROOT, run

sys.path.insert(0, os.path.join(ROOT, 'evals'))
import draft  # noqa: E402 (helpers put the scripts on sys.path)
from score import inventory, slide_root, text_lines, text_score  # noqa: E402


def true_texts(example, lines):
    """{reading line id: text} from the hand-made spec (its `from` references name the analysis pieces)."""
    with open(os.path.join(ROOT, 'examples', example, 'spec.json'), encoding='utf-8') as f:
        spec = json.load(f)
    where = {p: ln['id'] for ln in lines for p in ln['parts']}
    order = {ln['id']: k for k, ln in enumerate(lines)}
    texts, problems = {}, []
    for e in spec['elements']:
        if e['type'] not in ('text', 'bullets'):
            continue
        refs = e['from'] if isinstance(e['from'], list) else [e['from']]
        src = e.get('lines') or [t for it in e.get('items', []) for t in (it if isinstance(it, list) else [it])]
        for ref, t in zip(refs, src):
            t = t if isinstance(t, str) else ''.join(x if isinstance(x, str) else x.get('text', '') for x in t)
            ids = {where.get(p) for p in ref.split('+')} - {None}
            if len(ids) != 1:
                problems.append(f'{ref} -> reading lines {sorted(ids)}')
                if not ids:
                    continue
            texts[min(ids, key=order.get)] = t
    return texts, problems


class AutoBase:
    NAME = None

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d, ex = cls.tmp.name, os.path.join(ROOT, 'examples', cls.NAME)
        run('analyze.py', os.path.join(ex, 'source.png'), '--out', d)
        with open(os.path.join(d, 'analysis.json'), encoding='utf-8') as f:
            an = json.load(f)
        cls.lines, _ = draft.reading_lines(an)
        cls.texts, cls.problems = true_texts(cls.NAME, cls.lines)
        with open(os.path.join(d, 'texts.txt'), 'w', encoding='utf-8') as f:
            for ln in cls.lines:
                f.write(f"{ln['id']}: {cls.texts.get(ln['id'], '')}\n")
        run('draft.py', os.path.join(d, 'analysis.json'), os.path.join(d, 'texts.txt'), '--out', os.path.join(d, 'spec.json'))
        run('fit.py', os.path.join(d, 'spec.json'), '--out', os.path.join(d, 'spec.fitted.json'))
        cls.pptx = os.path.join(d, 'out', 'auto.pptx')
        run('build_pptx.py', os.path.join(d, 'spec.fitted.json'), '--out', cls.pptx)
        ref = next(f for f in sorted(os.listdir(ex)) if f.endswith('.pptx'))
        cls.ref_root, cls.got_root = slide_root(os.path.join(ex, ref)), slide_root(cls.pptx)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_reading_lines_match_the_slide(self):
        self.assertEqual(self.problems, [], 'every line of the hand-made spec is exactly one reading line')

    def test_same_text(self):
        score, cer, worst = text_score(text_lines(self.ref_root), text_lines(self.got_root))
        self.assertEqual(cer, 0, f'differences: {worst}')

    def test_same_objects(self):
        self.assertEqual(inventory(self.got_root), inventory(self.ref_root))


class AutoDemo(AutoBase, unittest.TestCase):
    NAME = 'demo'


class AutoArabic(AutoBase, unittest.TestCase):
    NAME = 'arabic'


class AutoJapanese(AutoBase, unittest.TestCase):
    NAME = 'japanese'


class AutoLanguages(AutoBase, unittest.TestCase):
    NAME = 'languages'


if __name__ == '__main__':
    unittest.main()
