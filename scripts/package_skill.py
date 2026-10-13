"""Build the uploadable skill archives.

    python scripts/package_skill.py [--out dist]

dist/unscreenshot.zip       the skill folder at the root of the zip (Claude, ChatGPT, Gemini, Copilot Studio...)
dist/unscreenshot-flat.zip  SKILL.md at the root of the zip, for uploaders that want it there

Archives are reproducible: sorted entries, fixed timestamps, no caches. The repository LICENSE is added as
LICENSE.txt so the archive stands on its own.
"""
import argparse
import hashlib
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = 'unscreenshot'
SKILL = os.path.join(ROOT, 'skills', NAME)
SKIP_DIRS = {'__pycache__', '.pytest_cache', 'work', 'out'}
SKIP_FILES = {'.DS_Store', 'Thumbs.db'}
EPOCH = (1980, 1, 1, 0, 0, 0)


def skill_files():
    files = []
    for d, dirs, names in os.walk(SKILL):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for n in names:
            if n in SKIP_FILES or n.endswith(('.pyc', '.pyo')):
                continue
            p = os.path.join(d, n)
            files.append((os.path.relpath(p, SKILL).replace(os.sep, '/'), p))
    files.append(('LICENSE.txt', os.path.join(ROOT, 'LICENSE')))
    return sorted(files)


def write_zip(path, prefix, files):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel, src in files:
            info = zipfile.ZipInfo(prefix + rel, EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if rel.endswith('.py') else 0o644) << 16
            with open(src, 'rb') as f:
                z.writestr(info, f.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'dist'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    files = skill_files()
    for fname, prefix in ((f'{NAME}.zip', NAME + '/'), (f'{NAME}-flat.zip', '')):
        path = os.path.join(a.out, fname)
        write_zip(path, prefix, files)
        with open(path, 'rb') as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        print(f'{path}  {os.path.getsize(path) // 1024} KB  {len(files)} files  sha256 {digest[:16]}')


if __name__ == '__main__':
    main()
