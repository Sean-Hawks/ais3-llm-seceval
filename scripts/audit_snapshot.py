#!/usr/bin/env python3
"""Compare local raw logs with the committed snapshot; publish only identities/hashes.

No prompts, transcripts, endpoint URLs, credentials or error bodies enter the audit.
Requires Inspect runtime dependencies and the original, unmodified local logs.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ais3_bench.data import ARMS, ROOT, read_json, row_key
from ais3_bench.logs import export_logs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--logs', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'output/snapshot_audit.json')
    args = parser.parse_args()
    source = ROOT / 'ctf/bench27/bench27_runs.json'
    old = {row_key(r): r for r in read_json(source)}
    with tempfile.TemporaryDirectory(prefix='ais3-log-audit-') as temp:
        destination = Path(temp) / 'export'
        export_logs(args.logs, destination)
        new = {row_key(r): r for r in read_json(destination / 'runs.json')}
        audit = read_json(destination / 'audit.json')
    if old.keys() != new.keys():
        raise SystemExit('Raw-log identities differ from snapshot; do not replace the published audit')
    fields = ('solved', 'score_value', 'scorer', 'target_flag', 'log_file', 'working_time', 'total_time')
    differences = [(k, f) for k in old for f in fields if old[k][f] != new[k][f]]
    differences += [(k, 'submitted[:400]') for k in old if old[k]['submitted'] != new[k]['submitted'][:400]]
    if differences:
        raise SystemExit(f'{len(differences)} value differences; investigate before publishing an audit')
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    files = {f'{arm}/{p.name}': sha(p) for arm in ARMS for p in sorted((args.logs / arm).glob('*.eval'))}
    exclusions = [r for r in audit['samples'] if r['status'] not in ('valid', 'superseded_run')]
    result = {
        'schema_version': 1,
        'description': 'Retrospective local raw-log audit, not evidence of preregistration or original network isolation.',
        'snapshot_sha256': sha(source),
        'compared_fields': [*fields, 'submitted[:400]'],
        'identity_match': True,
        'value_differences': 0,
        'sample_status_counts': dict(sorted(Counter(r['status'] for r in audit['samples']).items())),
        'excluded_samples': exclusions,
        'raw_logs_sha256': files,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: {len(old)} snapshot rows match raw logs; {len(exclusions)} exclusions; {len(files)} log hashes')


if __name__ == '__main__':
    main()
