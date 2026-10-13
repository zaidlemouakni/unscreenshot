"""Run the skill with several models on the example slides, headless, and score every result with score.py.

    python evals/run_models.py --plugin <plugin dir or .zip> --models claude-haiku-5-5 claude-opus-5-5 \
        --out <folder> [--cases demo arabic japanese languages] [--runs 1] [--run-budget 3] [--total-budget 15]

Each run is `claude -p` in its own empty folder holding only source.png, with the plugin loaded for that session
(--plugin-dir), no MCP server, and a shell limited to python, ls, mkdir, cp and cd. Runs stop being launched once
the spent total reaches --total-budget. Writes <out>/results.json and prints a table per model.
(`claude plugin eval` is the native way, but on Windows it refuses any shell tool because it cannot sandbox it.)
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from score import ROOT, score  # noqa: E402

PROMPT = ('Rebuild the slide in source.png (in the current folder) as an editable PowerPoint, identical. '
          'Save the result as slide.pptx in the current folder.')
TOOLS = ['Read', 'Write', 'Edit', 'Glob', 'Grep', 'Skill', 'Bash(python:*)', 'Bash(python3:*)', 'Bash(py:*)',
         'Bash(ls:*)', 'Bash(mkdir:*)', 'Bash(cp:*)', 'Bash(cd:*)']


def claude_exe():
    """The claude binary itself (on Windows `claude` is a .cmd wrapper that mangles JSON arguments)."""
    found = shutil.which('claude')
    if found and os.name == 'nt':
        exe = os.path.join(os.path.dirname(found), 'node_modules', '@anthropic-ai', 'claude-code', 'bin', 'claude.exe')
        if os.path.isfile(exe):
            return exe
    return found or 'claude'


def run_once(plugin, model, case, folder, budget, timeout):
    os.makedirs(folder, exist_ok=True)
    shutil.copy(os.path.join(ROOT, 'examples', case, 'source.png'), os.path.join(folder, 'source.png'))
    cmd = [claude_exe(), '-p', PROMPT, '--model', model, '--output-format', 'json', '--max-budget-usd', str(budget),
           '--plugin-dir', plugin, '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
           '--no-session-persistence', '--max-turns', '150', '--allowedTools', *TOOLS]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=folder, capture_output=True, text=True, encoding='utf-8', timeout=timeout)
        out = p.stdout
    except subprocess.TimeoutExpired as ex:
        out = ex.stdout or ''
        if isinstance(out, bytes):
            out = out.decode('utf-8', 'replace')
    info = {}
    try:
        info = json.loads(out.strip().splitlines()[-1]) if out.strip() else {}
    except (json.JSONDecodeError, IndexError):
        info = {'raw': out[-2000:]}
    with open(os.path.join(folder, 'claude.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    return {'cost': float(info.get('total_cost_usd') or 0), 'turns': info.get('num_turns'),
            'seconds': round(time.time() - t0), 'error': info.get('subtype') if info.get('is_error') else None,
            'last_message': (info.get('result') or '')[-500:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plugin', required=True)
    ap.add_argument('--models', nargs='+', required=True)
    ap.add_argument('--cases', nargs='+', default=['demo', 'arabic', 'japanese', 'languages'])
    ap.add_argument('--runs', type=int, default=1)
    ap.add_argument('--run-budget', type=float, default=3.0)
    ap.add_argument('--total-budget', type=float, default=15.0)
    ap.add_argument('--timeout', type=int, default=2700)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    results_path = os.path.join(a.out, 'results.json')
    results = json.load(open(results_path, encoding='utf-8')) if os.path.exists(results_path) else []
    spent = sum(r.get('cost', 0) for r in results)
    cache = tempfile.mkdtemp(prefix='score_')
    for model in a.models:
        for case in a.cases:
            for k in range(1, a.runs + 1):
                if any(r['model'] == model and r['case'] == case and r['run'] == k for r in results):
                    continue  # already done (the runner can be resumed)
                if spent >= a.total_budget:
                    print(f'budget reached (${spent:.2f}): {model} {case} #{k} not run')
                    continue
                folder = os.path.join(a.out, model, f'{case}-{k}')
                print(f'-> {model} {case} #{k} ...', flush=True)
                r = run_once(os.path.abspath(a.plugin), model, case, folder,
                             min(a.run_budget, a.total_budget - spent), a.timeout)
                s = score(case, os.path.join(folder, 'slide.pptx'), cache)
                r.update(model=model, case=case, run=k, folder=folder,
                         **{key: s.get(key) for key in ('score', 'text', 'cer', 'objects', 'visual', 'mad', 'error',
                                                         'worst_lines', 'inventory') if key in s})
                spent += r['cost']
                results.append(r)
                with open(results_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=1)
                print(f"   score {r.get('score')}  text {r.get('text')}  objects {r.get('objects')}  "
                      f"visual {r.get('visual')}  cost ${r['cost']:.2f}  turns {r['turns']}  {r['seconds']} s"
                      + (f"  ERROR {r.get('error')}" if r.get('error') else ''), flush=True)
    print(f'\ntotal spent ${spent:.2f}')
    for model in a.models:
        rows = [r for r in results if r['model'] == model]
        if rows:
            mean = lambda k: sum((r.get(k) or 0) for r in rows) / len(rows)  # noqa: E731
            print(f"{model:<22} runs {len(rows)}  score {mean('score'):.3f}  text {mean('text'):.3f}  "
                  f"objects {mean('objects'):.3f}  visual {mean('visual'):.3f}  cost ${sum(r['cost'] for r in rows):.2f}")


if __name__ == '__main__':
    main()
