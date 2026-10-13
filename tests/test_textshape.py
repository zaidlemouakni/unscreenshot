"""textshape.py: scripts, directions, font slots, Arabic joining, display order and ink measurement."""
import os
import unittest
from unittest import mock

import helpers  # noqa: F401 (puts the scripts on sys.path)
import textshape as T
from common import find_font_file, headline_metrics, load_font

SAMPLES = {  # text: (family, script, rtl, slot, guessed language)
    'Quarterly report': ('alphabetic', 'LATIN', False, 'latin', 'en-US'),
    'Tiếng Việt': ('alphabetic', 'LATIN', False, 'latin', 'vi-VN'),
    'Báo cáo hàng quý': ('alphabetic', 'LATIN', False, 'latin', 'en-US'),  # no Vietnamese-only letter
    'Квартальный отчёт': ('alphabetic', 'CYRILLIC', False, 'latin', 'ru-RU'),
    'Τριμηνιαία αναφορά': ('alphabetic', 'GREEK', False, 'latin', 'el-GR'),
    'التقرير الفصلي': ('arabic', 'ARABIC', True, 'cs', 'ar-SA'),
    'گزارش سه‌ماهه': ('arabic', 'ARABIC', True, 'cs', 'fa-IR'),
    'דוח רבעוני': ('hebrew', 'HEBREW', True, 'cs', 'he-IL'),
    '季度报告': ('cjk', 'CJK', False, 'ea', 'zh-CN'),
    '四半期レポート': ('cjk', 'CJK', False, 'ea', 'ja-JP'),
    '분기 보고서': ('cjk', 'HANGUL', False, 'ea', 'ko-KR'),
    'तिमाही रिपोर्ट': ('indic', 'DEVANAGARI', False, 'cs', 'hi-IN'),
    'รายงานรายไตรมาส': ('sea', 'THAI', False, 'cs', 'th-TH'),
}


class ScriptTest(unittest.TestCase):
    def test_profiles_and_languages(self):
        for text, (family, script, rtl, slot, lang) in SAMPLES.items():
            with self.subTest(text=text):
                p = T.profile(text)
                self.assertEqual((p['family'], p['script'], p['rtl'], p['slot']), (family, script, rtl, slot))
                self.assertEqual(T.guess_lang(text, 'en-US'), lang)

    def test_slide_language_is_kept_when_it_fits(self):
        self.assertEqual(T.guess_lang('Rapport trimestriel', 'fr-FR'), 'fr-FR')
        self.assertEqual(T.guess_lang('التقرير', 'ar-EG'), 'ar-EG')
        self.assertEqual(T.guess_lang('2027', 'ja-JP'), 'ja-JP')          # no letters: the slide language
        self.assertEqual(T.guess_lang('Hello', 'ar-SA'), 'en-US')         # Latin words in an Arabic slide
        self.assertEqual(T.guess_lang('گزارش', 'ar-SA'), 'fa-IR')         # Persian letters
        self.assertEqual(T.guess_lang('日本語', 'zh-CN'), 'zh-CN')         # Han only: cannot tell, keep the slide's

    def test_full_width_text(self):
        self.assertTrue(T.profile('四半期レポート')['fullwidth'])
        self.assertFalse(T.profile('第3四半期')['fullwidth'])           # an ASCII digit is proportional
        self.assertFalse(T.profile('분기 보고서')['fullwidth'])

    def test_font_slots(self):
        self.assertEqual(T.slot_fonts('Arial', 'Hello'), {'latin': 'Arial', 'ea': 'Arial', 'cs': 'Arial'})
        self.assertEqual(T.slot_fonts('Arial', 'العربية')['cs'], 'Arial')               # Arial draws Arabic
        self.assertEqual(T.slot_fonts('Century Gothic', 'العربية')['cs'], 'Segoe UI')   # it does not
        self.assertEqual(T.slot_fonts('Arial', '四半期レポート', 'ja-JP')['ea'], 'Yu Gothic')
        self.assertEqual(T.slot_fonts('Arial', '季度报告', 'zh-TW')['ea'], 'Microsoft JhengHei')
        self.assertEqual(T.slot_fonts('Arial', 'हिन्दी')['cs'], 'Nirmala UI')
        self.assertEqual(T.slot_fonts('Yu Gothic', 'EV バン')['ea'], 'Yu Gothic')
        self.assertEqual(T.slot_fonts('Arial', 'ไทย', font_cs='Tahoma')['cs'], 'Tahoma')
        self.assertEqual(T.measuring_font('Segoe UI', 'דוח רבעוני'), 'Segoe UI')


class ArabicTest(unittest.TestCase):
    def test_contextual_forms(self):
        # seen, lam-alef ligature (final form after a joining letter), meem isolated
        self.assertEqual(T.arabic_shape('سلام'), 'ﺳﻼﻡ')
        # beh initial, beh medial, beh final; isolated alone; marks are transparent
        self.assertEqual(T.arabic_shape('ببب'), 'ﺑﺒﺐ')
        self.assertEqual(T.arabic_shape('ب'), 'ﺏ')
        self.assertEqual(T.arabic_shape('بَب'), 'ﺑَﺐ')
        # zero width non-joiner breaks the join (Persian)
        self.assertEqual(T.arabic_shape('ب‌ب'), 'ﺏ‌ﺏ')
        self.assertEqual(T.arabic_shape('Hello'), 'Hello')

    def test_display_order(self):
        self.assertEqual(T.visual('٦٠٪', True), '٪٦٠')                   # percent left of Arabic-Indic digits
        self.assertEqual(T.visual('٦٠٪', False), '٦٠٪')
        self.assertEqual(T.visual('AB 12', False), 'AB 12')
        self.assertEqual(T.visual('אב 12', True), '12 בא')                 # numbers stay left-to-right
        self.assertEqual(T.visual('AI في 2027', True), '2027 يف AI')
        self.assertEqual(T.visual('بَب', True), 'ببَ')                     # a mark stays with its letter

    def test_paragraph_direction(self):
        self.assertTrue(T.paragraph_rtl('التقرير'))
        self.assertFalse(T.paragraph_rtl('Hello'))
        self.assertTrue(T.paragraph_rtl('٦٠٪', lang='ar-SA'))              # no letters: the slide's language
        self.assertFalse(T.paragraph_rtl('٦٠٪', lang='en-US'))
        self.assertFalse(T.paragraph_rtl('التقرير', direction='ltr'))


class MeasureTest(unittest.TestCase):
    def font(self, family):
        path, exact, _ = find_font_file(family)
        if not (path and exact):
            self.skipTest(f'{family} not installed here')
        return path

    def test_ink_is_not_the_layout_box(self):
        f = load_font(self.font('Arial'), 200)
        x0, top, x1, bottom = T.ink_extents(f, ' Hello ')
        self.assertGreater(x0, 50)                     # the leading space and the H's left bearing are not ink
        self.assertLess(x1 - x0, f.getlength(' Hello ') - 100)
        self.assertLess(top, -130)
        self.assertEqual(T.ink_extents(f, ' ')[2], 0.0)

    def test_methods(self):
        arial = self.font('Arial')
        with mock.patch.dict(os.environ, {'UNSCREENSHOT_NO_RAQM': '1'}):
            self.assertEqual(T.measure(arial, 'Hello', 100)['method'], 'basic')
            m = T.measure(arial, 'مرحبا بالعالم', 100)
            self.assertEqual((m['method'], m['width_ok']), ('arabic-joiner', True))
            joined, apart = m['x1'] - m['x0'], T.ink_extents(load_font(arial, 100), 'مرحبا بالعالم')
            self.assertLess(joined, 0.85 * (apart[2] - apart[0]))  # joined letters are much narrower
        if T.raqm_available():
            self.assertEqual(T.measure(arial, 'Hello', 100)['method'], 'raqm')

    def test_indic_without_shaping_is_flagged(self):
        nirmala = self.font('Nirmala UI')
        with mock.patch.dict(os.environ, {'UNSCREENSHOT_NO_RAQM': '1'}):
            m = T.measure(nirmala, 'तिमाही रिपोर्ट', 100)
            self.assertFalse(m['width_ok'])
            b = T.bands(nirmala, 'तिमाही रिपोर्ट', 100)
            self.assertLess(b['headline_top'], -50)        # the headline hangs well above the baseline
            self.assertAlmostEqual(b['body_bottom'], 0, delta=2)

    def test_headline_metrics(self):
        rows = [0, 5, 6, 40, 42, 41, 12, 11, 13, 12, 11, 12, 3, 1, 0]
        top, bottom = headline_metrics(rows)
        self.assertAlmostEqual(top, 3 - 6 / 40, places=3)  # the partly covered row above counts as a fraction
        self.assertAlmostEqual(bottom, 12 + 3 / 11.5, places=3)  # body = median of the rows below: 11.5
        self.assertIsNone(headline_metrics([0, 0, 0]))

    def test_missing_glyphs(self):
        arial = self.font('Arial')
        self.assertEqual(T.missing_glyphs(arial, 'Hello'), [])
        self.assertEqual(T.missing_glyphs(arial, 'A日'), ['日'])


if __name__ == '__main__':
    unittest.main()
