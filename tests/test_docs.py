"""Translated docs stay complete and in sync with the English ones: one README and one install guide per language
of the flag bar, the same commands, every relative link and image resolving, right-to-left pages marked."""
import os
import re
import unittest

from helpers import ROOT

LANGS = ['fr', 'zh-CN', 'es', 'pt-BR', 'ja', 'vi', 'ko', 'fa', 'th', 'ar']
RTL = {'fa', 'ar'}


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding='utf-8') as f:
        return f.read()


def readme(code):
    return read('.github', 'readme', f'README.{code}.md')


def install(code):
    return read('.github', 'install', f'INSTALL.{code}.md')


def fenced(text):
    return [m.group(0) for m in re.finditer(r'```\w*\n.*?```', text, re.S)]


def command_spans(text):
    """Inline code that is an install command or a skills folder (identical in every language)."""
    prose = re.sub(r'```\w*\n.*?```', '', text, flags=re.S)
    return sorted({s for s in re.findall(r'`([^`\n]+)`', prose)
                   if re.match(r'(claude|codex|gemini|npx|qwen|git|cp) ', s) or s.startswith(('~/', '.vibe', '.agents'))})


def targets(text):
    """Relative link and image targets of a Markdown/HTML page."""
    out = re.findall(r'\]\(([^)\s]+)\)', text) + re.findall(r'(?:href|src)="([^"]+)"', text)
    return [t.split('#')[0] for t in out if not t.startswith(('http://', 'https://', 'mailto:', '#')) and t.split('#')[0]]


class DocsTest(unittest.TestCase):
    def test_every_language_has_both_pages(self):
        for code in LANGS:
            with self.subTest(lang=code):
                self.assertTrue(os.path.isfile(os.path.join(ROOT, '.github', 'readme', f'README.{code}.md')))
                self.assertTrue(os.path.isfile(os.path.join(ROOT, '.github', 'install', f'INSTALL.{code}.md')))

    def test_flag_bars_list_every_language(self):
        english = read('README.md')
        for code in LANGS:
            self.assertIn(f'.github/readme/README.{code}.md', english)
            self.assertIn(f'.github/install/INSTALL.{code}.md', read('INSTALL.md'))
        for code in LANGS:
            with self.subTest(lang=code):
                page = readme(code)
                self.assertIn('href="../../README.md"', page)
                for other in LANGS:
                    if other != code:
                        self.assertIn(f'href="README.{other}.md"', page)
                self.assertIn('[English](../../INSTALL.md)', install(code))

    def test_install_commands_match_english(self):
        english = fenced(read('INSTALL.md'))
        self.assertEqual(len(english), 11)
        for code in LANGS:
            with self.subTest(lang=code):
                self.assertEqual(fenced(install(code)), english)
                self.assertEqual(command_spans(install(code)), command_spans(read('INSTALL.md')))

    def test_readme_commands_match_english(self):
        english = command_spans(read('README.md'))
        self.assertIn('claude plugin install unscreenshot@unscreenshot', english)
        for code in LANGS:
            with self.subTest(lang=code):
                self.assertEqual(command_spans(readme(code)), english)

    def test_links_and_images_resolve(self):
        pages = [('README.md',), ('INSTALL.md',), ('AGENTS.md',), ('CONTRIBUTING.md',), ('SECURITY.md',),
                 ('CODE_OF_CONDUCT.md',), ('.github', 'pull_request_template.md')]
        pages += [('.github', 'readme', f'README.{c}.md') for c in LANGS]
        pages += [('.github', 'install', f'INSTALL.{c}.md') for c in LANGS]
        for parts in pages:
            base = os.path.dirname(os.path.join(ROOT, *parts))
            for t in targets(read(*parts)):
                with self.subTest(page='/'.join(parts), target=t):
                    self.assertTrue(os.path.exists(os.path.normpath(os.path.join(base, t))))

    def test_readmes_show_the_demo_and_the_sample(self):
        pages = [('README.md', read('README.md'))] + [(code, readme(code)) for code in LANGS]
        for name, page in pages:
            with self.subTest(page=name):
                self.assertIn('docs/demo.gif)', page)
                self.assertIn('examples/demo/source.png)', page)

    def test_comparison_table_matches_english(self):
        def marks(page):
            return re.findall(r'✅|❌|⚠️', page)
        english = marks(read('README.md'))
        self.assertEqual(len(english), 5 * 4 + 1)  # 5 rows x 4 columns, and the legend
        for code in LANGS:
            with self.subTest(lang=code):
                self.assertEqual(marks(readme(code)), english)

    def test_right_to_left_pages(self):
        for code in RTL:
            with self.subTest(lang=code):
                for page in (readme(code), install(code)):
                    self.assertIn('<div dir="rtl">', page)
                    self.assertTrue(page.rstrip().endswith('</div>'))

    def test_no_template_leftovers(self):
        for code in LANGS:
            for page in (readme(code), install(code)):
                with self.subTest(lang=code):
                    self.assertIsNone(re.search(r'\{(zip|a|b|cmd|install|en|contrib|ar|ja|lg|skill|release|sample)\}', page))


if __name__ == '__main__':
    unittest.main()
