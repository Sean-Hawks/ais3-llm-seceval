#!/usr/bin/env python3
"""Check maintained documentation links and bilingual guide parity, offline."""
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
files = [ROOT / name for name in ('README.md', 'README.en.md', 'README.zh-TW.md', 'AUTHORS.md', 'RECOGNITION.md', 'CHANGELOG.md',
                                  'CONTRIBUTING.md', 'SECURITY.md', 'THIRD_PARTY_NOTICES.md')]
files += [ROOT / 'docs/README.md', ROOT / 'docs/SETUP.md']
files += list((ROOT / 'docs/en').glob('*.md')) + list((ROOT / 'docs/zh-TW').glob('*.md'))
files += list((ROOT / 'results').glob('*.md'))
files += [ROOT / 'results/figures/README.md']
files += [ROOT / name for name in ('ctf/README.md', 'ctf/bench27/README.md',
                                   'ctf/bench27/recent2026/SERVICE_WIRING.md',
                                   'docs/history/README.md', 'docs/REPORT_前置作業.md',
                                   'docs/SLIDES_環境與踩雷.md')]
files += list((ROOT / 'ctf/bench27/deep_hard').glob('*/README.md'))
errors = []
for path in files:
    text = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
    for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        if href.startswith(('http:', 'https:', 'mailto:', '#')):
            continue
        target = unquote(href.split('#')[0].strip('<>'))
        if target and not (path.parent / target).exists():
            errors.append(f'{path.relative_to(ROOT)}: missing link {href}')
zh = {p.name for p in (ROOT / 'docs/zh-TW').glob('*.md')}
en = {p.name for p in (ROOT / 'docs/en').glob('*.md')}
if zh != en:
    errors.append(f'Bilingual guide mismatch: {zh ^ en}')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(files)} maintained documents; {len(en)} bilingual guide pairs; local links resolve')
