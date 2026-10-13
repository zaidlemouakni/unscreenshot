"""Skill metadata, manifests and portability rules that every platform relies on."""
import glob
import io
import json
import os
import re
import tokenize
import unittest

from helpers import DEMO, ROOT, SCRIPTS, SKILL

NAME = 'unscreenshot'


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding='utf-8') as f:
        return f.read().replace('\r\n', '\n')


def frontmatter(text):
    assert text.startswith('---\n'), 'SKILL.md must start with YAML frontmatter'
    head = text[4:text.index('\n---', 4)]
    data, parent = {}, None
    for line in head.splitlines():
        if not line.strip():
            continue
        key, _, value = line.strip().partition(':')
        value = value.strip().strip('"\'')
        if line.startswith((' ', '\t')) and parent:
            data[parent][key] = value
        elif value:
            data[key], parent = value, None
        else:
            data[key], parent = {}, key
    return data


def quote_of(tok):
    body = tok.lstrip('rRbBuUfF')
    return body[0], body[:3] in ('"""', "'''")


class MetadataTest(unittest.TestCase):
    def setUp(self):
        self.skill_md = read('skills', NAME, 'SKILL.md')
        self.fm = frontmatter(self.skill_md)

    def test_frontmatter(self):
        self.assertEqual(self.fm['name'], NAME)
        self.assertEqual(os.path.basename(SKILL), NAME)
        self.assertRegex(NAME, r'^[a-z0-9]+(-[a-z0-9]+)*$')
        self.assertLessEqual(len(NAME), 64)
        desc = self.fm['description']
        self.assertGreater(len(desc), 80)
        self.assertLessEqual(len(desc), 500, 'keep it short: some uploaders cap descriptions (spec limit is 1024)')
        self.assertNotRegex(desc, r'[<>]', 'no angle brackets in the description (rejected by some uploaders)')
        self.assertEqual(self.fm['license'], 'MIT')
        self.assertRegex(self.fm['metadata']['version'], r'^\d+\.\d+\.\d+$')

    def test_versions_are_aligned(self):
        version = self.fm['metadata']['version']
        for path in ('.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'gemini-extension.json',
                     'qwen-extension.json'):
            with self.subTest(manifest=path):
                self.assertEqual(json.loads(read(path))['version'], version)
        self.assertEqual(re.search(r'^## (\d+\.\d+\.\d+)', read('CHANGELOG.md'), re.M).group(1), version)

    def test_manifests(self):
        for path in glob.glob(os.path.join(ROOT, '**', '*.json'), recursive=True):
            if os.sep + 'examples' + os.sep in path or os.sep + 'reference' + os.sep in path or 'work' in path:
                continue
            with self.subTest(json=os.path.relpath(path, ROOT)):
                with open(path, encoding='utf-8') as f:
                    json.load(f)
        claude = json.loads(read('.claude-plugin/marketplace.json'))
        self.assertEqual([p['name'] for p in claude['plugins']], [NAME])
        self.assertEqual(claude['plugins'][0]['source'], './')
        codex = json.loads(read('.codex-plugin/plugin.json'))
        self.assertTrue(os.path.isdir(os.path.join(ROOT, codex['skills'])))
        for key in ('composerIcon', 'logo'):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, codex['interface'][key])), key)
        self.assertEqual([p['name'] for p in json.loads(read('.agents/plugins/marketplace.json'))['plugins']], [NAME])
        for ext in ('gemini-extension.json', 'qwen-extension.json'):
            m = json.loads(read(ext))
            self.assertEqual(m['name'], NAME)
            self.assertTrue(os.path.isfile(os.path.join(ROOT, m['contextFileName'])))
        self.assertIn(f'${NAME}', read('skills', NAME, 'agents', 'openai.yaml'))

    def test_skill_md_points_at_real_files(self):
        mentioned = set(re.findall(r'scripts/([a-z_]+\.py)', self.skill_md))
        self.assertTrue(mentioned)
        for name in mentioned:
            self.assertTrue(os.path.isfile(os.path.join(SCRIPTS, name)), name)
        for name in re.findall(r'reference/([\w.-]+\.(?:md|json))', self.skill_md):
            self.assertTrue(os.path.isfile(os.path.join(SKILL, 'reference', name)), name)
        # tool scripts are documented in SKILL.md or in the reference guides it points to
        for ref in glob.glob(os.path.join(SKILL, 'reference', '*.md')):
            with open(ref, encoding='utf-8') as f:
                mentioned |= set(re.findall(r'scripts/([a-z_]+\.py)', f.read()))
        tools = {os.path.basename(p) for p in glob.glob(os.path.join(SCRIPTS, '*.py'))} - {
            'common.py', 'fontmatch.py', 'pptx_writer.py', 'textshape.py'}
        self.assertEqual(tools - mentioned, set(), 'every tool script is documented in SKILL.md or reference/')

    def test_scripts_make_no_network_calls(self):
        banned = re.compile(r'^\s*(?:import|from)\s+(urllib|requests|http|socket|ftplib|smtplib|httpx|aiohttp)\b', re.M)
        for path in glob.glob(os.path.join(SCRIPTS, '*.py')):
            with self.subTest(script=os.path.basename(path)):
                with open(path, encoding='utf-8') as f:
                    self.assertIsNone(banned.search(f.read()))

    def test_scripts_run_on_python_310(self):
        """Python 3.12 relaxed f-string quoting; sandboxes still run 3.10/3.11."""
        if not hasattr(tokenize, 'FSTRING_START'):
            return  # this interpreter is < 3.12 and already compiled the scripts
        for path in glob.glob(os.path.join(SCRIPTS, '*.py')) + glob.glob(os.path.join(ROOT, 'scripts', '*.py')):
            with open(path, encoding='utf-8') as f:
                src = f.read()
            stack = []
            for t in tokenize.generate_tokens(io.StringIO(src).readline):
                if t.type in (tokenize.FSTRING_START, tokenize.STRING) and stack:
                    q = quote_of(t.string)
                    for outer in stack:
                        clash = q[0] == outer[0] and (not outer[1] or q[1])
                        self.assertFalse(clash, f'{os.path.basename(path)}:{t.start[0]} reuses the enclosing quote')
                    if t.type == tokenize.STRING:
                        self.assertNotIn('\\', t.string, f'{os.path.basename(path)}:{t.start[0]} backslash in an f-string expression')
                if t.type == tokenize.FSTRING_START:
                    stack.append(quote_of(t.string))
                elif t.type == tokenize.FSTRING_END:
                    stack.pop()

    def test_example_spec_is_the_demo(self):
        with open(os.path.join(SKILL, 'reference', 'example-spec.json'), encoding='utf-8') as f:
            ref = json.load(f)
        with open(os.path.join(DEMO, 'spec.json'), encoding='utf-8') as f:
            self.assertEqual(ref, json.load(f))


if __name__ == '__main__':
    unittest.main()
