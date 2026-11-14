"""Fehlerpfadtests für den echten Portabel-Ordner-Vertrag; keine Windows-Simulation als HOST-PASS."""
from pathlib import Path
import tempfile,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from VERIFY_PORTABLE_FOLDER import verify,APP
with tempfile.TemporaryDirectory() as t:
    folder=Path(t)
    fail=verify(folder,platform='linux')
    assert fail['status']=='FAIL' and len(fail['errors'])>=9
    for rel in (APP+'.exe','assets/app.ico','assets/banner.png','assets/logo.png','tools/ffmpeg.exe',
                'tools/ffprobe.exe','BEDIENUNGSANLEITUNG_DE.md','MANUAL_EN.md','REPARATUR_AUDIO_TOOLS.bat','PORTABLE_VERIFY.bat','PORTABLE_VERIFY.ps1'):
        f=folder/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b'MZ' if rel.endswith('.exe') else b'x')
    (folder/'_internal').mkdir()
    static=verify(folder,platform='linux')
    assert static['status']=='STATIC_PASS_WINDOWS_PENDING',static
    (folder/'tools/ffprobe.exe').unlink()
    assert verify(folder,platform='linux')['status']=='FAIL'
print('PASS portable check: missing components fail, static success does not claim Windows runtime')
