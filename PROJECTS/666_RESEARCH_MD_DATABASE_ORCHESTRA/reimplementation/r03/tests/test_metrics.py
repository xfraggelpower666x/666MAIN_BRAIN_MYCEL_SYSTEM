from __future__ import annotations
import unittest
import hashlib
import json
from unittest.mock import patch
from helpers import R03TestBase, analyzer, write_wav
from src import wav_io, analysis_stem

class Tests(R03TestBase):
    def test_valid_two_stem_analysis_reports_expected_schema_and_pair(self):
        kick = self.stem('kick', frequency=50.0, amplitude=0.7)
        bass = self.stem('bass', frequency=55.0, amplitude=0.45)
        report = self.analyze(kick, bass)
        self.assertEqual(report['schema'], analyzer.SCHEMA)
        self.assertEqual(report['status'], 'ANALYSIS_COMPLETE_HEURISTIC_MASKING_ONLY')
        self.assertEqual(len(report['stems']), 2)
        self.assertEqual(len(report['pairwise']), 1)
        self.assertIn('sub_20_60', report['stems'][0]['bands'])
        self.assertFalse(report['resource_limits']['source_files_loaded_whole'])
        json.dumps(report, allow_nan=False)

    def test_same_band_has_more_spectral_overlap_than_separated_bands(self):
        kick = self.stem('kick', frequency=50.0)
        bass = self.stem('bass', frequency=55.0)
        same = self.analyze(kick, bass)['pairwise'][0]['spectral_overlap_percent']
        (self.root / 'bass.wav').unlink()
        bass = self.stem('bass', frequency=1000.0)
        separated = self.analyze(kick, bass)['pairwise'][0]['spectral_overlap_percent']
        self.assertGreater(same, separated)

    def test_heuristic_is_explicitly_not_a_psychoacoustic_threshold_model(self):
        report = self.analyze(self.stem('kick', frequency=50), self.stem('bass', frequency=50))
        self.assertIn('not a validated psychoacoustic masking threshold', report['method']['masking_index_is_not'])
        self.assertEqual(report['method']['level_unit'], 'dBFS, not LUFS')

    def test_all_six_roles_are_accepted_and_missing_roles_are_reported(self):
        specs = [self.stem(role, frequency=100 + i * 100) for i, role in enumerate(analyzer.ALLOWED_ROLES)]
        report = self.analyze(*specs)
        self.assertEqual(len(report['stems']), 6)
        self.assertEqual(len(report['pairwise']), 15)
        self.assertEqual(report['input']['roles_missing'], [])

    def test_source_audio_sha256_is_reported_for_provenance(self):
        kick = self.stem("kick", frequency=50.0)
        bass = self.stem("bass", frequency=1000.0)
        report = self.analyze(kick, bass)
        item = next(x for x in report["stems"] if x["role"] == "kick")
        expected = hashlib.sha256((self.root / "kick.wav").read_bytes()[44:]).hexdigest()
        self.assertEqual(item["source_sha256_analyzed_audio_bytes"], expected)
        self.assertGreater(item["analysis_windows"], 0)

    def test_stereo_correlation_detects_antiphase(self):
        self.stem('kick', channels=2, inverted_right=True)
        self.stem('bass', channels=2, inverted_right=False)
        report = self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))
        kick = next(x for x in report['stems'] if x['role'] == 'kick')
        bass = next(x for x in report['stems'] if x['role'] == 'bass')
        self.assertLess(kick['stereo_correlation'], -0.99)
        self.assertEqual(kick['mono_compatibility'], 'WATCH_NEGATIVE_CORRELATION')
        self.assertGreater(bass['stereo_correlation'], 0.99)

    def test_mono_has_no_stereo_correlation_claim(self):
        report = self.analyze(self.stem('kick'), self.stem('bass', frequency=50))
        self.assertIsNone(report['stems'][0]['stereo_correlation'])

    def test_full_scale_clipping_is_reported(self):
        report = self.analyze(self.stem('kick', amplitude=1.0), self.stem('bass', amplitude=0.2))
        kick = next(x for x in report['stems'] if x['role'] == 'kick')
        self.assertGreater(kick['clipped_sample_count'], 0)

    def test_input_byte_guard_blocks_before_analysis(self):
        self.stem('kick')
        self.stem('bass')
        with patch.object(wav_io, 'MAX_TOTAL_INPUT_BYTES', 1):
            with self.assertRaisesRegex(analyzer.AnalysisError, 'TOTAL_INPUT_BYTES_LIMIT_EXCEEDED'):
                self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))

    def test_working_memory_estimate_is_bounded(self):
        self.stem('kick', channels=2)
        self.stem('bass', channels=2)
        with patch.object(analysis_stem, 'MAX_WORKING_MEMORY_BYTES', 1024):
            with self.assertRaisesRegex(analyzer.AnalysisError, 'FFT_WORKING_MEMORY_GUARD'):
                self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))
