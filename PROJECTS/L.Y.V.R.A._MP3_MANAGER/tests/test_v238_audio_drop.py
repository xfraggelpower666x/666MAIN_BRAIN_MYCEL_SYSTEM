"""Audio-Browser-Dispatch mit Tcl und echten Pfaden; der Explorer bleibt ein Host-Test."""
from pathlib import Path
import runpy
from types import SimpleNamespace
import tkinter as tk
from unittest.mock import Mock


def test_audio_drop_accepts_mixed_files_with_conflicting_filters(tmp_path):
    manager = Path(__file__).resolve().parents[1] / 'MP3_Manager.pyw'
    app_class = runpy.run_path(str(manager))['App']
    tcl = tk.Tcl()
    wav = tmp_path / 'A B.wav'
    mp3 = tmp_path / 'C D.mp3'
    for path in (wav, mp3):
        path.touch()
    browser = SimpleNamespace(
        root=SimpleNamespace(tk=tcl, after_idle=lambda func: func()),
        input_kind=tk.StringVar(tcl, 'wav'), audio_filter=tk.StringVar(tcl, 'missing'),
        wav_folder=tk.StringVar(tcl), folder=tk.StringVar(tcl),
        audio_tree=Mock(), on_audio_selection=Mock(), status=Mock(),
    )

    def refresh():
        assert browser.input_kind.get() == 'mixed'
        assert browser.audio_filter.get() == ''
        browser.audio_paths = {'wav': wav, 'mp3': mp3}

    browser.refresh_audio_browser = refresh
    app_class.audio_drop(browser, SimpleNamespace(data=f'{{{wav}}} {{{mp3}}}'))
    assert browser.wav_folder.get() == str(tmp_path)
    browser.audio_tree.selection_set.assert_called_once_with(['wav', 'mp3'])
    browser.status.set.assert_not_called()
