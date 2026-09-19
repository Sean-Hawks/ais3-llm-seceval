"""Publication boundaries and identities, with no Hub login or network calls."""

import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from ais3_bench.data import load_snapshot, row_key
from ais3_bench.hub import hub_artifacts, write_hub_export


class HubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = hub_artifacts()
        cls.tables = {name: [json.loads(line) for line in cls.outputs[f'data/{name}.jsonl'].decode().splitlines()]
                      for name in ('attempts', 'tasks', 'exclusions')}

    def test_complete_projection_preserves_scores_and_missing_slots(self):
        self.assertEqual({k: len(v) for k, v in self.tables.items()},
                         {'attempts': 803, 'tasks': 27, 'exclusions': 7})
        original = {row_key(r): r['score_value'] for r in load_snapshot()[1]}
        self.assertEqual({row_key(r): r['score_value'] for r in self.tables['attempts']}, original)
        keys = [row_key(r) for r in self.tables['attempts'] + self.tables['exclusions']]
        self.assertEqual(len(set(keys)), 810)
        self.assertEqual(sum(r['working_time_anomaly'] for r in self.tables['attempts']), 1)

    def test_export_does_not_include_sensitive_or_third_party_content(self):
        forbidden = {'target_flag', 'submitted', 'flag', 'log_file', 'messages', 'transcript', 'files', 'service', 'api_key'}
        flags = [p['flag'] for p in load_snapshot()[0]['problems']]
        for table in self.tables.values():
            for row in table:
                self.assertFalse(set(row) & forbidden)
        for name, data in self.outputs.items():
            if name.endswith(('.json', '.jsonl', '.md')):
                text = data.decode()
                self.assertFalse(any(flag in text for flag in flags), name)
        self.assertEqual(set(self.outputs), {'README.md', 'data/attempts.jsonl', 'data/tasks.jsonl',
            'data/exclusions.jsonl', 'provenance.json', 'figures/outcomes.png', 'CITATION.cff', 'CITATION.bib',
            'LICENSE', 'THIRD_PARTY_NOTICES.md', 'SHA256SUMS'})

    def test_changed_source_requires_a_new_publication_version(self):
        with patch('ais3_bench.hub.source_hashes', return_value={}):
            with self.assertRaisesRegex(ValueError, 'Source snapshot changed'):
                hub_artifacts()

    def test_bundle_is_deterministic_and_never_overwrites(self):
        self.assertEqual(self.outputs, hub_artifacts())
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'dataset'
            write_hub_export(output)
            before = {str(p.relative_to(output)): p.read_bytes() for p in output.rglob('*') if p.is_file()}
            with self.assertRaises(ValueError):
                write_hub_export(output)
            self.assertEqual(before, self.outputs)
            for line in self.outputs['SHA256SUMS'].decode().splitlines():
                digest, name = line.split('  ', 1)
                self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), digest)

    def test_dataset_card_links_and_destination(self):
        card = self.outputs['README.md'].decode()
        self.assertNotIn('__DATASET_ID__', card)
        for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)', card):
            if not href.startswith(('https:', '#')):
                self.assertIn(href, self.outputs)
        custom = hub_artifacts(repo_id='research-team/bench27')['README.md'].decode()
        self.assertIn('load_dataset("research-team/bench27"', custom)
        with self.assertRaises(ValueError):
            hub_artifacts(repo_id='../invalid')


if __name__ == '__main__':
    unittest.main()
