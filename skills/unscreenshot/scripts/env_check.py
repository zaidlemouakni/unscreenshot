"""Report what this sandbox can do for the slide rebuild: libraries, renderers, and which Office fonts are
metric-exact here (the real font or a metric-compatible twin). Run it once at the start of every job.

    python scripts/env_check.py [--json work/env.json]
"""
import argparse
import importlib
import os
import platform
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import METRIC_TWINS, find_font_file, powerpoint_available, save_json, which  # noqa: E402
from fit import measuring_file  # noqa: E402
from textshape import profile, raqm_available, slot_fonts  # noqa: E402

SCRIPTS = [('Chinese', '季度报告', 'zh-CN'), ('Japanese', '四半期レポート', 'ja-JP'), ('Korean', '분기 보고서', 'ko-KR'),
           ('Arabic', 'التقرير الفصلي', 'ar-SA'), ('Persian', 'گزارش فصلی', 'fa-IR'), ('Hebrew', 'דוח רבעוני', 'he-IL'),
           ('Hindi', 'तिमाही रिपोर्ट', 'hi-IN'), ('Thai', 'รายงานรายไตรมาส', 'th-TH')]

OFFICE_FONTS = ['Arial', 'Calibri', 'Aptos', 'Segoe UI', 'Century Gothic', 'Cambria', 'Georgia', 'Times New Roman',
                'Verdana', 'Tahoma', 'Trebuchet MS', 'Courier New', 'Arial Narrow', 'Century Schoolbook',
                'Bookman Old Style']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default=None)
    a = ap.parse_args()
    rep = {'python': sys.version.split()[0], 'platform': platform.platform(), 'modules': {}, 'tools': {}, 'fonts': {}}
    for mod in ('PIL', 'numpy', 'scipy', 'fitz', 'pypdfium2'):
        try:
            m = importlib.import_module(mod)
            rep['modules'][mod] = getattr(m, '__version__', 'ok')
        except Exception:
            rep['modules'][mod] = None
    for tool in ('soffice', 'libreoffice', 'pdftoppm', 'fc-match'):
        rep['tools'][tool] = which(tool)
    rep['tools']['powerpoint'] = 'windows-com' if powerpoint_available() else None
    for fam in OFFICE_FONTS:
        path, exact, resolved = find_font_file(fam)
        rep['fonts'][fam] = {'exact_metrics': bool(exact), 'resolved': resolved, 'file': path}

    rep['shaping'] = 'raqm' if raqm_available() else 'none (built-in Arabic joiner; Indic scripts sized on their height)'
    rep['scripts'] = {}
    for name, sample, lang in SCRIPTS:
        fam = slot_fonts('Arial', sample, lang)[profile(sample)['slot']]
        path, exact, resolved = measuring_file(fam, sample, lang)
        rep['scripts'][name] = {'office_font': fam, 'measured_with': resolved, 'exact': bool(exact), 'file': path}

    print('Python', rep['python'], '|', rep['platform'])
    print('Modules:', ', '.join(f"{k}={'OK ' + str(v) if v else 'missing'}" for k, v in rep['modules'].items()))
    print('Tools:  ', ', '.join(f"{k}={'OK' if v else 'missing'}" for k, v in rep['tools'].items()))
    ok = [f for f, v in rep['fonts'].items() if v['exact_metrics']]
    print('Metric-exact fonts here:', ', '.join(ok) or 'none')
    print('Others (substituted; sizes will be estimated from cap height):',
          ', '.join(f"{f}->{v['resolved'] or '?'}" for f, v in rep['fonts'].items() if not v['exact_metrics']))
    must = [m for m in ('PIL', 'numpy') if not rep['modules'][m]]
    if must:
        print('BLOCKING: missing modules', must, '-> try `pip install pillow numpy`; without them the skill cannot run.')
    if not (rep['tools']['soffice'] or rep['tools']['libreoffice'] or rep['tools']['powerpoint']):
        print('No renderer (LibreOffice/PowerPoint): check.py needs --render-png, otherwise compare visually.')
    print('Text shaping:', rep['shaping'])
    print('Scripts:', ', '.join(
        f"{n}=" + ('exact (' + v['office_font'] + ')' if v['exact'] else
                   'approx (' + v['measured_with'] + ')' if v['measured_with'] else 'NO FONT (cap height only)')
        for n, v in rep['scripts'].items()))
    print('Known metric twins:', '; '.join(f"{k} = {' / '.join(v)}" for k, v in METRIC_TWINS.items()))
    if a.json:
        save_json(rep, a.json)


if __name__ == '__main__':
    main()
