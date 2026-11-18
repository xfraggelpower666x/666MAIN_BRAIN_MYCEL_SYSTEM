"""Fehlerpfadtests für den echten Portabel-Ordner-Vertrag; keine Windows-Simulation als HOST-PASS."""
from pathlib import Path
import tempfile,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from VERIFY_PORTABLE_FOLDER import verify,REQUIRED_FILES
with tempfile.TemporaryDirectory() as t:
    folder=Path(t)
    fail=verify(folder,platform='linux')
    assert fail['status']=='FAIL' and len(fail['errors'])>=9
    for rel in REQUIRED_FILES:
        f=folder/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b'MZ' if rel.endswith('.exe') else b'x')
    static=verify(folder,platform='linux')
    assert static['status']=='STATIC_PASS_WINDOWS_PENDING',static
    (folder/'tools/ffprobe.exe').write_bytes(b'not a Windows program')
    assert verify(folder,platform='linux')['status']=='FAIL'
    (folder/'tools/ffprobe.exe').unlink()
    assert verify(folder,platform='linux')['status']=='FAIL'
print('PASS portable check: missing components fail, static success does not claim Windows runtime')
