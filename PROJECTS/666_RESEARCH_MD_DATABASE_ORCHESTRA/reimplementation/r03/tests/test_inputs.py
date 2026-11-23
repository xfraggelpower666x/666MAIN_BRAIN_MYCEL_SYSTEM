from __future__ import annotations
import unittest
from pathlib import Path
from unittest.mock import patch
from helpers import R03TestBase, analyzer, write_wav
from src import wav_io

class Tests(R03TestBase):
    def test_duplicate_role_is_rejected(self):
        a = self.stem('kick')
        with self.assertRaisesRegex(analyzer.AnalysisError, 'DUPLICATE_STEM_ROLE'):
            self.analyze(a, a)

    def test_same_source_file_cannot_be_registered_as_two_roles(self):
        a = self.stem("kick")
        with self.assertRaisesRegex(analyzer.AnalysisError, "DUPLICATE_STEM_FILE"):
            self.analyze(a, ("bass", "kick.wav"))

    def test_unknown_role_is_rejected(self):
        write_wav(self.root / 'synth.wav')
        with self.assertRaisesRegex(analyzer.AnalysisError, 'UNKNOWN_STEM_ROLE'):
            self.analyze(('synth', 'synth.wav'), self.stem('kick'))

    def test_too_few_or_too_many_stems_are_rejected(self):
        a = self.stem('kick')
        with self.assertRaisesRegex(analyzer.AnalysisError, 'INVALID_STEM_COUNT'):
            self.analyze(a)
        six = [self.stem(role) for role in analyzer.ALLOWED_ROLES]
        with patch.object(wav_io, 'MAX_STEMS', 5):
            with self.assertRaisesRegex(analyzer.AnalysisError, 'INVALID_STEM_COUNT'):
                self.analyze(*six)

    def test_missing_stem_file_is_rejected(self):
        self.stem('kick')
        with self.assertRaises(FileNotFoundError):
            self.analyze(('kick', 'kick.wav'), ('bass', 'missing.wav'))

    def test_path_traversal_is_blocked(self):
        outside = Path(self.temp.name) / 'outside.wav'
        write_wav(outside)
        self.stem('kick')
        with self.assertRaisesRegex(analyzer.AnalysisError, 'PATH_TRAVERSAL_BLOCKED'):
            self.analyze(('kick', 'kick.wav'), ('bass', '../outside.wav'))

    def test_symlink_escape_is_blocked(self):
        outside = Path(self.temp.name) / 'outside.wav'
        write_wav(outside)
        try:
            (self.root / 'escape.wav').symlink_to(outside)
        except OSError:
            self.skipTest("Symlink creation is not permitted by this Windows host")
        self.stem('kick')
        with self.assertRaisesRegex(analyzer.AnalysisError, 'STEM_PATH_ESCAPES_INPUT_ROOT'):
            self.analyze(('kick', 'kick.wav'), ('bass', 'escape.wav'))

    def test_non_wav_container_is_rejected(self):
        self.stem('kick')
        (self.root / 'bass.mp3').write_bytes(b'not-a-wave')
        with self.assertRaisesRegex(analyzer.AnalysisError, 'UNSUPPORTED_AUDIO_CONTAINER'):
            self.analyze(('kick', 'kick.wav'), ('bass', 'bass.mp3'))

    def test_malformed_wav_is_rejected(self):
        self.stem('kick')
        (self.root / 'bass.wav').write_bytes(b'RIFF\x00\x00\x00\x00WAVEbad')
        with self.assertRaisesRegex(analyzer.AnalysisError, 'INVALID_OR_UNREADABLE_WAV'):
            self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))

    def test_truncated_wav_data_is_rejected(self):
        self.stem('kick')
        write_wav(self.root / 'bass.wav', duration=1.0)
        p = self.root / 'bass.wav'
        p.write_bytes(p.read_bytes()[:-256])
        with self.assertRaisesRegex(analyzer.AnalysisError, 'TRUNCATED_WAV_DATA'):
            self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))

    def test_sample_rate_mismatch_is_blocked(self):
        self.stem('kick', sample_rate=44100)
        self.stem('bass', sample_rate=48000)
        with self.assertRaisesRegex(analyzer.AnalysisError, 'SAMPLE_RATE_MISMATCH'):
            self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))

    def test_duration_mismatch_over_one_second_is_blocked(self):
        self.stem('kick', duration=1.0)
        self.stem('bass', duration=2.1)
        with self.assertRaisesRegex(analyzer.AnalysisError, 'DURATION_MISMATCH_EXCEEDS_TOLERANCE'):
            self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))

    def test_duration_difference_within_tolerance_is_explicitly_reported(self):
        self.stem('kick', duration=1.0)
        self.stem('bass', duration=1.75)
        report = self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))
        self.assertAlmostEqual(report['input']['comparison_duration_seconds'], 1.0, places=4)
        bass = next(x for x in report['stems'] if x['role'] == 'bass')
        self.assertAlmostEqual(bass['excluded_tail_seconds'], 0.75, places=3)

    def test_duration_guard_blocks_before_streaming(self):
        self.stem('kick', duration=1.0)
        self.stem('bass', duration=1.0)
        with patch.object(wav_io, 'MAX_DURATION_SECONDS', 0.5):
            with self.assertRaisesRegex(analyzer.AnalysisError, 'DURATION_LIMIT_EXCEEDED'):
                self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))

    def test_sample_rate_bounds_are_enforced(self):
        self.stem('kick', sample_rate=4000)
        self.stem('bass', sample_rate=4000)
        with self.assertRaisesRegex(analyzer.AnalysisError, 'SAMPLE_RATE_OUT_OF_RANGE'):
            self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))

    def test_three_channel_input_is_rejected(self):
        self.stem('kick')
        self.stem('bass', channels=3)
        with self.assertRaisesRegex(analyzer.AnalysisError, 'UNSUPPORTED_CHANNEL_COUNT'):
            self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))

    def test_pcm_8_16_24_and_32_bit_are_supported(self):
        for width in (1, 2, 3, 4):
            (self.root / 'kick.wav').unlink(missing_ok=True)
            (self.root / 'bass.wav').unlink(missing_ok=True)
            self.stem('kick', width=width, frequency=50)
            self.stem('bass', width=width, frequency=1000)
            report = self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))
            self.assertEqual(report['stems'][0]['pcm_bits'], width * 8)

    def test_role_filename_parser_is_strict(self):
        self.assertEqual(analyzer.parse_stem_spec('kick=kick.wav'), ('kick', 'kick.wav'))
        for value in ('kick', '=kick.wav', 'snare=snare.wav', 'kick='):
            with self.assertRaises(analyzer.AnalysisError):
                analyzer.parse_stem_spec(value)
