"""R5.5 offline regression: relocation suggestions never alter originals."""
import hashlib
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from archive_source_relocation import propose_relocations, RelocationError

def setup(tmp_path, records):
    src = tmp_path / 'sources'; src.mkdir()
    cp = tmp_path / 'checkpoint.json'
    cp.write_text(json.dumps({'schema': '666.chatbackup.batch-checkpoint.v1', 'completed': records}))
    return src, cp

def h(b): return hashlib.sha256(b).hexdigest()

def test_unchanged(tmp_path):
    src, cp = setup(tmp_path, {'a.zip': h(b'zip')})
    (src/'a.zip').write_bytes(b'zip')
    assert propose_relocations(src, cp)['sources'][0]['status'] == 'VERIFIED'

def test_relocated_and_read_only(tmp_path):
    src, cp = setup(tmp_path, {'old.zip': h(b'zip')})
    (src/'new.zip').write_bytes(b'zip')
    before = cp.read_bytes()
    report = propose_relocations(src, cp)
    assert report['sources'][0]['status'] == 'RELOCATED_CANDIDATE'
    assert report['sources'][0]['candidates'] == ['new.zip']
    assert cp.read_bytes() == before and (src/'new.zip').read_bytes() == b'zip'

def test_ambiguous(tmp_path):
    src, cp = setup(tmp_path, {'old.zip': h(b'zip')})
    (src/'one.zip').write_bytes(b'zip'); (src/'two.zip').write_bytes(b'zip')
    assert propose_relocations(src, cp)['sources'][0]['status'] == 'AMBIGUOUS'

def test_changed_does_not_promote_other_copy(tmp_path):
    src, cp = setup(tmp_path, {'old.zip': h(b'zip')})
    (src/'old.zip').write_bytes(b'changed')
    (src/'new.zip').write_bytes(b'zip')
    assert propose_relocations(src, cp)['sources'][0]['status'] == 'CHANGED'

def test_missing(tmp_path):
    src, cp = setup(tmp_path, {'old.zip': h(b'zip')})
    assert propose_relocations(src, cp)['sources'][0]['status'] == 'MISSING'

@pytest.mark.parametrize('name', ['../escape.zip', '/absolute.zip', 'bad\\windows.zip', 'C:drive.zip', 'bad.txt'])
def test_invalid_checkpoint_names(tmp_path, name):
    src, cp = setup(tmp_path, {name: h(b'zip')})
    with pytest.raises(RelocationError): propose_relocations(src, cp)

def test_symlink_not_followed(tmp_path):
    src, cp = setup(tmp_path, {'old.zip': h(b'zip')})
    outside = tmp_path/'outside.zip'; outside.write_bytes(b'zip')
    (src/'linked.zip').symlink_to(outside)
    assert propose_relocations(src, cp)['sources'][0]['status'] == 'MISSING'


def test_recursive_relocation_and_flat_mode(tmp_path):
    src, cp = setup(tmp_path, {'old.zip': h(b'nested')})
    nested = src / 'renamed' / 'nested'; nested.mkdir(parents=True)
    (nested / 'new.zip').write_bytes(b'nested')
    assert propose_relocations(src, cp)['sources'][0]['candidates'] == ['renamed/nested/new.zip']
    assert propose_relocations(src, cp, recursive=False)['sources'][0]['status'] == 'MISSING'


@pytest.mark.parametrize('digest', ['xyz', 'g' * 64, 123, None])
def test_invalid_digest_is_rejected(tmp_path, digest):
    src, cp = setup(tmp_path, {'original.zip': digest})
    with pytest.raises(RelocationError, match='Invalid checkpoint'):
        propose_relocations(src, cp)


@pytest.mark.parametrize('raw', ['{broken', '[]', '{"schema":"wrong","completed":{}}'])
def test_malformed_checkpoint_fails_closed(tmp_path, raw):
    src, cp = setup(tmp_path, {})
    cp.write_text(raw, encoding='utf-8')
    with pytest.raises(RelocationError):
        propose_relocations(src, cp)


def test_invalid_utf8_checkpoint_fails_closed(tmp_path):
    src, cp = setup(tmp_path, {})
    cp.write_bytes(bytes([255, 254]))
    with pytest.raises(RelocationError, match='Invalid checkpoint JSON'):
        propose_relocations(src, cp)


def test_checkpoint_byte_limit(tmp_path, monkeypatch):
    import archive_source_relocation as module
    src, cp = setup(tmp_path, {})
    monkeypatch.setattr(module, 'MAX_CHECKPOINT_BYTES', 16)
    saved = cp.read_bytes()
    with pytest.raises(RelocationError, match='size limit'):
        propose_relocations(src, cp)
    assert cp.read_bytes() == saved


def test_scan_limit_counts_non_zip_entries(tmp_path, monkeypatch):
    import archive_source_relocation as module
    src, cp = setup(tmp_path, {})
    for index in range(3):
        (src / f'other-{index}.txt').write_text('data')
    monkeypatch.setattr(module, 'MAX_SCAN_ENTRIES', 2)
    with pytest.raises(RelocationError, match='entry limit'):
        propose_relocations(src, cp)


def test_no_recursion_into_directory_symlink(tmp_path):
    src, cp = setup(tmp_path, {'old.zip': h(b'nested')})
    elsewhere = tmp_path / 'elsewhere'; elsewhere.mkdir()
    (elsewhere / 'copy.zip').write_bytes(b'nested')
    try:
        (src / 'link').symlink_to(elsewhere, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip('Directory symlinks unavailable on this host')
    assert propose_relocations(src, cp)['sources'][0]['status'] == 'MISSING'
