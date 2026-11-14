"""Virtueller Tk-Test des Auswahlzustandes, ausdrücklich kein Windows-DnD-Test."""
import pathlib,runpy,tempfile,tkinter as tk
from pathlib import Path
ns=runpy.run_path(str(Path(__file__).resolve().parents[1]/'MP3_Manager.pyw'),run_name='v236_test')
root=tk.Tk()
try:
    app=ns['App'](root)
    with tempfile.TemporaryDirectory() as tmp:
        a=Path(tmp)/'A';b=Path(tmp)/'B';a.mkdir();b.mkdir()
        (a/'one.wav').write_bytes(b'fake');(a/'two.wav').write_bytes(b'fake')
        (b/'new.wav').write_bytes(b'fake')
        app.input_kind.set('wav')
        app.wav_folder.set(str(a));app.refresh_audio_browser()
        assert len(app.audio_tree.selection())==2,'first folder must select all'
        app.audio_select_none();app.refresh_audio_browser()
        assert not app.audio_tree.selection(),'explicit empty choice must be preserved'
        app.wav_folder.set(str(b));app.refresh_audio_browser()
        assert len(app.audio_tree.selection())==1,'new folder must auto-select new entry'
        print('PASS: folder change selects new file; explicit empty selection preserved on refresh')
finally:root.destroy()
