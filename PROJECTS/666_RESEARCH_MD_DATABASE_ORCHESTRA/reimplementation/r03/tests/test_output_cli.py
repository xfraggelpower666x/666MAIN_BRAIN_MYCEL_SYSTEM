from __future__ import annotations
import unittest
import json
from pathlib import Path
from helpers import R03TestBase, analyzer, write_wav
from cli import main as cli_main

class Tests(R03TestBase):
    def test_analysis_does_not_write_files(self):
        self.stem('kick')
        self.stem('bass')
        before = sorted(p.name for p in self.root.iterdir())
        self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))
        after = sorted(p.name for p in self.root.iterdir())
        self.assertEqual(before, after)

    def test_output_inside_input_is_blocked(self):
        self.stem('kick')
        self.stem('bass')
        report = self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))
        with self.assertRaisesRegex(analyzer.AnalysisError, 'OUTPUT_DIRECTORY_MUST_NOT_BE_INSIDE_INPUT'):
            analyzer.write_report(report, self.root / 'out', self.root)

    def test_report_write_is_atomic_and_no_silent_overwrite(self):
        self.stem('kick')
        self.stem('bass')
        report = self.analyze(('kick', 'kick.wav'), ('bass', 'bass.wav'))
        output = Path(self.temp.name) / 'reports'
        target = analyzer.write_report(report, output, self.root)
        self.assertTrue(target.is_file())
        parsed = json.loads(target.read_text(encoding='utf-8'))
        self.assertEqual(parsed['schema'], analyzer.SCHEMA)
        with self.assertRaisesRegex(analyzer.AnalysisError, 'OUTPUT_EXISTS_USE_FORCE'):
            analyzer.write_report(report, output, self.root)
        analyzer.write_report(report, output, self.root, force=True)
        self.assertEqual(list(output.glob('.stem-analysis-r03-*.tmp')), [])

    def test_cli_stdout_and_output_folder(self):
        self.stem('kick')
        self.stem('bass')
        from io import StringIO
        import contextlib
        stdout = StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli_main(['--input', str(self.root), '--stem', 'kick=kick.wav', '--stem', 'bass=bass.wav'])
        self.assertEqual(code, 0)
        self.assertIn('ANALYSIS_COMPLETE_HEURISTIC_MASKING_ONLY', stdout.getvalue())
        outdir = Path(self.temp.name) / 'cli-report'
        with contextlib.redirect_stdout(stdout):
            code = cli_main(['--input', str(self.root), '--stem', 'kick=kick.wav', '--stem', 'bass=bass.wav', '--output', str(outdir)])
        self.assertEqual(code, 0)
        self.assertTrue((outdir / 'stem-analysis-r03.json').is_file())
