"""R5.5 user-facing Archive Intelligence source relocation entry points."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'tools' / 'archive_intelligence_cli.py'
GUI = ROOT / 'tools' / 'archive_intelligence_gui.py'


def test_cli_relocate_sources_end_to_end(tmp_path):
    sources = tmp_path / 'exports'
    sources.mkdir()
    archive = sources / 'moved.zip'
    archive.write_bytes(b'untouched archive')
    expected = hashlib.sha256(archive.read_bytes()).hexdigest()
    checkpoint = tmp_path / 'checkpoint.json'
    checkpoint.write_text(json.dumps({
        'schema': '666.chatbackup.batch-checkpoint.v1',
        'completed': {'before.zip': expected}
    }), encoding='utf-8')
    before = (archive.read_bytes(), checkpoint.read_bytes())
    command = [sys.executable, str(CLI), 'relocate-sources', str(sources), str(checkpoint)]
    output = subprocess.run(command, capture_output=True, text=True, timeout=40, check=False)
    assert output.returncode == 0, output.stderr
    report = json.loads(output.stdout)
    assert report['schema'] == '666.chatbackup.source-relocation.v1'
    assert report['sources'][0]['status'] == 'RELOCATED_CANDIDATE'
    assert report['sources'][0]['candidates'] == ['moved.zip']
    assert (archive.read_bytes(), checkpoint.read_bytes()) == before


def test_cli_bad_checkpoint_reports_blocked(tmp_path):
    folder = tmp_path / 'exports'
    folder.mkdir()
    checkpoint = tmp_path / 'checkpoint.json'
    checkpoint.write_text('{malformed', encoding='utf-8')
    output = subprocess.run(
        [sys.executable, str(CLI), 'relocate-sources', str(folder), str(checkpoint)],
        capture_output=True, text=True, timeout=40, check=False
    )
    assert output.returncode == 2
    assert 'ARCHIVE_BLOCKED' in output.stderr


def test_cli_relocate_flat_mode(tmp_path):
    folder = tmp_path / 'exports'
    nested = folder / 'sub'
    nested.mkdir(parents=True)
    (nested / 'found.zip').write_bytes(b'archive')
    checkpoint = tmp_path / 'checkpoint.json'
    checkpoint.write_text(json.dumps({
        'schema': '666.chatbackup.batch-checkpoint.v1',
        'completed': {'previous.zip': hashlib.sha256(b'archive').hexdigest()}
    }), encoding='utf-8')
    run = subprocess.run(
        [sys.executable, str(CLI), 'relocate-sources', str(folder), str(checkpoint), '--flat'],
        capture_output=True, text=True, timeout=40, check=False
    )
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)['sources'][0]['status'] == 'MISSING'


def test_gui_exposes_relocation_without_starting_tk_window():
    # Import module only; no GUI instantiation on headless CI.
    spec = importlib.util.spec_from_file_location('archive_intelligence_gui_r55_test', GUI)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.ArchiveWindow.find_moved_sources)
    nested = [value for value in module.ArchiveWindow.find_moved_sources.__code__.co_consts
              if isinstance(value, types.CodeType)]
    assert any('propose_relocations' in code.co_names for code in nested)
