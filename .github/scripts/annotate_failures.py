"""Turn the failures in a `python -m unittest -v` log into GitHub Actions error annotations, so they show on
the run's summary page and in pull requests without opening the logs. Usage: annotate_failures.py <log>"""
import os
import re
import sys


def escape(text, prop=False):
    text = text.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    return text.replace(':', '%3A').replace(',', '%2C') if prop else text


def main(path):
    if not os.path.exists(path):
        print(f'::error title=Tests::no test log ({path}): the tests did not start')
        return
    with open(path, encoding='utf-8', errors='replace') as f:
        log = f.read()
    shown = 0
    for block in re.split(r'^={50,}$', log, flags=re.M):
        block = block.strip()
        if not block.startswith(('FAIL: ', 'ERROR: ')):
            continue
        title = block.splitlines()[0]
        parts = block.split('-' * 70)  # header / traceback / (last block only) the run summary
        traceback = parts[1] if len(parts) > 1 else parts[0]
        lines = [l for l in traceback.splitlines() if l.strip() and not set(l.strip()) <= set('~^')]
        detail = '\n'.join(lines[-4:])  # the failing line and the assertion message
        if shown < 9:  # GitHub shows 10 error annotations per step: keep one for the summary
            print(f'::error title={escape(title, prop=True)}::{escape(detail)}')
        shown += 1
    summary = [l for l in log.splitlines() if re.match(r'(Ran \d+ tests|FAILED|OK)', l)]
    print(f"::error title=Tests::{escape(' '.join(summary[-2:]) or 'the test run stopped early')}"
          + (f' ({shown - 9} more failures in the log)' if shown > 9 else ''))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'test-output.txt')
