import re
from pathlib import Path

files = [f for f in Path('.').glob('*.py')
         if not f.name.startswith('_check') and not f.name.startswith('_audit')
         and not f.name.startswith('_review') and not f.name.startswith('_scan')]

issues = []
for f in files:
    text = f.read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        if not re.search(r'2026-0[5-9]-\d{2}', line):
            continue
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        skip_words = ['TODAY', 'datetime', 'REVENUE_DATE', 'FOMC_DATE', 'PRICE_DATE', 'BWIBBU_DATE', '_FOMC', 'timedelta']
        if any(w in line for w in skip_words):
            continue
        issues.append((f.name, i, stripped[:90]))

if issues:
    for fname, lineno, line in issues[:25]:
        print(f'{fname}:{lineno}: {line}')
else:
    print('No remaining hardcoded 2026 dates found in production scripts')
