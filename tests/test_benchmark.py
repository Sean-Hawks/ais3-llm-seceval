"""Offline behavioral regression tests; no network, Docker or model calls."""

import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
import tempfile
import unittest
from unittest.mock import patch
import sys

from ais3_bench.data import ROOT, aggregate, load_snapshot, read_json, row_key, validate_repository, validate_rows
from ais3_bench.logs import authored_text, export_logs, invalid_reason, select_latest
from ais3_bench.report import artifacts, write_reports
from ais3_bench.runner import commands
from ais3_bench.scoring import exact_flag_match


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.rows, cls.config = load_snapshot()
        cls.summary = aggregate(cls.manifest, cls.rows, cls.config)

    def test_repository_assets_and_joins(self):
        self.assertEqual(validate_repository(), [])

    def test_reproduces_six_model_task_coverage(self):
        self.assertEqual({r['model']: r['solved_tasks'] for r in self.summary['models']},
                         {'8b': 4, '12b': 12, '26b': 14, '30b': 10, '70b': 7, '550b': 15})

    def test_missing_attempts_are_explicit(self):
        self.assertEqual(self.summary['valid_attempts'], 803)
        self.assertEqual(self.summary['expected_attempts'], 810)
        self.assertEqual(len(self.summary['missing_attempts']), 7)
        self.assertEqual(len({tuple(r.values()) for r in self.summary['missing_attempts']}), 7)

    def test_raw_log_audit_explains_each_missing_attempt(self):
        audit = read_json(ROOT / 'ctf/bench27/snapshot_audit.json')
        self.assertEqual({row_key(r) for r in audit['excluded_samples']},
                         {row_key(r) for r in self.summary['missing_attempts']})
        self.assertEqual(audit['sample_status_counts'],
                         {'sample_error': 3, 'zero_generation': 4, 'valid': 803, 'superseded_run': 60})

    def test_published_figure_uses_current_validated_summary(self):
        inputs = read_json(ROOT / 'results/figures/inputs.json')
        self.assertEqual(inputs['summary_sha256'], hashlib.sha256(artifacts()['summary.json'].encode()).hexdigest())

    def test_summed_time_is_stable_across_python_versions_and_row_order(self):
        self.assertEqual(self.summary['summed_sample_hours'], 80.55611111111111)
        reversed_summary = aggregate(self.manifest, list(reversed(self.rows)), self.config)
        self.assertEqual(reversed_summary['summed_sample_hours'], self.summary['summed_sample_hours'])

    def test_different_model_denominators(self):
        totals = {r['model']: r['valid_attempts'] for r in self.summary['models']}
        self.assertEqual(totals, {'8b': 132, '12b': 131, '26b': 135, '30b': 135, '70b': 135, '550b': 135})

    def test_negative_telemetry_is_preserved_and_flagged(self):
        anomalies = self.summary['telemetry_anomalies']
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]['value'], -1340.8)

    def test_gap_uses_unrounded_attempt_rates(self):
        model = next(r for r in self.summary['models'] if r['model'] == '12b')
        self.assertAlmostEqual(model['gap_percentage_points'], 100 * (33 / 60 - 14 / 57))

    def test_duplicate_attempt_is_rejected(self):
        errors = validate_rows(self.rows + [self.rows[0]], self.manifest, self.config)
        self.assertTrue(any('duplicate' in e for e in errors))

    def test_string_boolean_is_rejected(self):
        row = {**self.rows[0], 'solved': 'false'}
        self.assertTrue(any('boolean' in e for e in validate_rows([row], self.manifest, self.config)))

    def test_mismatched_score_is_rejected(self):
        row = {**self.rows[0], 'solved': not self.rows[0]['solved']}
        self.assertTrue(any('disagrees' in e for e in validate_rows([row], self.manifest, self.config)))

    def test_unknown_task_is_rejected(self):
        row = {**self.rows[0], 'task': 'unknown-task'}
        self.assertTrue(validate_rows([row], self.manifest, self.config))

    def test_target_unicode_change_is_rejected(self):
        row = {**self.rows[0], 'target_flag': self.rows[0]['target_flag'] + 'x'}
        self.assertTrue(any('target' in e for e in validate_rows([row], self.manifest, self.config)))

    def test_nan_time_is_rejected(self):
        row = {**self.rows[0], 'working_time': float('nan')}
        self.assertTrue(any('working_time' in e for e in validate_rows([row], self.manifest, self.config)))

    def test_new_negative_time_is_rejected(self):
        row = {**self.rows[0], 'working_time': -2}
        self.assertTrue(any('working_time' in e for e in validate_rows([row], self.manifest, self.config)))

    def test_missing_arm_has_null_accuracy_not_zero(self):
        summary = aggregate(self.manifest, [], self.config)
        self.assertIsNone(summary['models'][0]['arms']['recent2026']['accuracy'])
        self.assertIsNone(summary['models'][0]['gap_percentage_points'])

    def test_report_is_deterministic_and_detects_staleness(self):
        with tempfile.TemporaryDirectory() as directory:
            write_reports(directory)
            before = {p.name: p.read_bytes() for p in Path(directory).iterdir()}
            write_reports(directory)
            self.assertEqual(before, {p.name: p.read_bytes() for p in Path(directory).iterdir()})
            write_reports(directory, check=True)
            (Path(directory) / 'summary.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'Stale'):
                write_reports(directory, check=True)


class FlagTests(unittest.TestCase):
    def test_correct_flag_with_prose(self):
        self.assertTrue(exact_flag_match('The flag is lactf{correct}.', 'lactf{correct}'))

    def test_candidate_bombing_is_rejected(self):
        self.assertFalse(exact_flag_match('lactf{wrong} lactf{correct}', 'lactf{correct}'))

    def test_duplicates_of_same_flag_are_allowed(self):
        self.assertTrue(exact_flag_match('lactf{correct} lactf{correct}', 'lactf{correct}'))

    def test_unicode_homoglyph_is_not_normalized(self):
        self.assertFalse(exact_flag_match('lactf{gооd}', 'lactf{good}'))

    def test_case_is_preserved(self):
        self.assertFalse(exact_flag_match('LACTF{correct}', 'lactf{correct}'))

    def test_empty_submission_fails(self):
        self.assertFalse(exact_flag_match('', 'lactf{correct}'))

    def test_long_flags_are_not_silently_truncated(self):
        flag = 'AIS3{' + 'x' * 250 + '}'
        self.assertTrue(exact_flag_match(flag, flag))


class LogTests(unittest.TestCase):
    def test_only_assistant_authored_content_is_extracted(self):
        sample = NS(messages=[NS(role='system', text='SECRET_SYSTEM'), NS(role='user', text='SECRET_PROMPT'),
                              NS(role='tool', text='SECRET_OBSERVED'),
                              NS(role='assistant', text='Reasoning', tool_calls=[NS(arguments={'command': 'ls /challenge'})])])
        self.assertEqual(authored_text(sample), 'Reasoning\nls /challenge')

    def test_latest_invalid_run_does_not_fall_back_to_older_success(self):
        groups = [('recent2026', 'task', '8b', '2026-01-01.eval', ['old success']),
                  ('recent2026', 'task', '8b', '2026-02-01.eval', ['new error'])]
        self.assertEqual(select_latest(groups)[('recent2026', 'task', '8b')][1], ['new error'])

    def test_latest_single_epoch_replaces_old_five_epoch_run(self):
        groups = [('deep_hard', 'task', '8b', '2026-01-01.eval', [1, 2, 3, 4, 5]),
                  ('deep_hard', 'task', '8b', '2026-02-01.eval', [1])]
        self.assertEqual(select_latest(groups)[('deep_hard', 'task', '8b')][1], [1])

    def test_zero_generation_is_invalid(self):
        self.assertEqual(invalid_reason(NS(error=None, messages=[NS(role='user')])), 'zero_generation')

    def test_error_is_invalid_even_with_assistant_messages(self):
        self.assertEqual(invalid_reason(NS(error=True, messages=[NS(role='assistant')])), 'sample_error')

    def test_missing_score_is_not_counted_as_incorrect(self):
        self.assertEqual(invalid_reason(NS(error=None, messages=[NS(role='assistant')], scores={})),
                         'missing_or_unsupported_score')


class RunnerTests(unittest.TestCase):
    def test_full_plan_has_24_jobs(self):
        self.assertEqual(len(commands('all', 'all')), 24)

    def test_all_arms_share_experiment_limits(self):
        for command in commands('all', 'all'):
            for option, value in [('--epochs', '5'), ('--message-limit', '50'), ('--time-limit', '1800')]:
                self.assertEqual(command[command.index(option) + 1], value)
            self.assertIn('--no-parallel-tool-calls', command)
            self.assertIn('/output/runs/preview/', command[command.index('--log-dir') + 1])

    def test_prefix_is_configurable(self):
        command = commands('recent2026', '8b', prefix='openai-api/example/')[0]
        self.assertEqual(command[command.index('--model') + 1], 'openai-api/example/llama-3.1-8b')

    def test_nonpositive_epochs_rejected(self):
        with self.assertRaises(ValueError):
            commands('recent2026', '8b', epochs=0)

    def test_epoch_override_is_shared_by_all_jobs(self):
        for command in commands('all', '8b', epochs=1):
            self.assertEqual(command[command.index('--epochs') + 1], '1')


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.logs = self.root / 'logs'
        (self.logs / 'recent2026').mkdir(parents=True)
        self.output = self.root / 'export'

    def sample(self, epoch=1, error=None):
        return NS(id='rev_ooo', epoch=epoch, error=error,
                  messages=[NS(role='user', text='PROMPT'), NS(role='assistant', text='reasoning')],
                  scores={'exact_flag': NS(value='C')}, target='lactf{ok}',
                  output=NS(completion='lactf{ok}'), working_time=1.0, total_time=2.0)

    def fake_reader(self, logs):
        def read(path):
            return NS(eval=NS(model='openai-api/ais3/ais3/llama-3.1-8b'), samples=logs[Path(path).name])
        return patch.dict(sys.modules, {'inspect_ai.log': NS(read_eval_log=read)})

    def make_logs(self, mapping):
        for name in mapping:
            (self.logs / 'recent2026' / name).touch()

    def test_empty_logs_leave_existing_evidence_untouched(self):
        self.output.mkdir()
        sentinel = self.output / 'runs.json'
        sentinel.write_text('keep')
        with self.fake_reader({}), self.assertRaisesRegex(ValueError, 'No .eval'):
            export_logs(self.logs, self.output)
        self.assertEqual(sentinel.read_text(), 'keep')

    def test_new_run_exclusions_are_audited_without_old_epoch_fallback(self):
        old = [self.sample(i) for i in range(1, 6)]
        new = [self.sample(1, error=True), self.sample(2)]
        mapping = {'2026-01-01.eval': old, '2026-02-01.eval': new}
        self.make_logs(mapping)
        with self.fake_reader(mapping):
            self.assertEqual(export_logs(self.logs, self.output), 1)
        rows = json.loads((self.output / 'runs.json').read_text())
        self.assertEqual([r['epoch'] for r in rows], [2])
        audit = json.loads((self.output / 'audit.json').read_text())
        self.assertEqual([r['status'] for r in audit['samples']], ['superseded_run'] * 5 + ['sample_error', 'valid'])
        authored = (self.output / 'authored.jsonl').read_text()
        self.assertNotIn('PROMPT', authored)
        self.assertIn('reasoning', authored)

    def test_no_valid_attempt_does_not_create_output(self):
        mapping = {'2026-01-01.eval': [self.sample(error=True)]}
        self.make_logs(mapping)
        with self.fake_reader(mapping), self.assertRaisesRegex(ValueError, 'No valid'):
            export_logs(self.logs, self.output)
        self.assertFalse(self.output.exists())

    def test_duplicate_epoch_aborts_export(self):
        mapping = {'2026-01-01.eval': [self.sample(), self.sample()]}
        self.make_logs(mapping)
        with self.fake_reader(mapping), self.assertRaisesRegex(ValueError, 'Duplicate epoch'):
            export_logs(self.logs, self.output)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
