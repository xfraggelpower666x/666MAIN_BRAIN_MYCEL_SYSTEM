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

@pytest.mark.parametrize('name', ['../escape.zip', '/absolute.zip', 'bad\\windows.zip', 'bad.txt'])
def test_invalid_checkpoint_names(tmp_path, name):
    src, cp = setup(tmp_path, {name: h(b'zip')})
    with pytest.raises(RelocationError): propose_relocations(src, cp)

def test_symlink_not_followed(tmp_path):
    src, cp = setup(tmp_path, {'old.zip': h(b'zip')})
    outside = tmp_path/'outside.zip'; outside.write_bytes(b'zip')
    (src/'linked.zip').symlink_to(outside)
    assert propose_relocations(src, cp)['sources'][0]['status'] == 'MISSING'
