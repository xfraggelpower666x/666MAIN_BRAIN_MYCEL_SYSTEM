import runpy
import sys
import time
import tkinter as tk
import wave
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_restoration_overlay_handoff(tmp_path):
    source = tmp_path / "source.wav"
    with wave.open(str(source), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(44100)
        output.writeframes(b"\0\0" * 44100)
    original = source.read_bytes()
    namespace = runpy.run_path(str(ROOT / "MP3_Manager.pyw"), run_name="overlay_test")
    root = tk.Tk()
    app = namespace["App"](root)
    try:
        app.input_kind.set("wav")
        app.wav_folder.set(str(tmp_path))
        app.refresh_audio_browser()
        app.open_restoration_overlay()
        overlay = app.restoration_app
        deadline = time.monotonic() + 30
        while overlay.restoration is None and overlay.busy and time.monotonic() < deadline:
            root.update()
            time.sleep(.02)
        assert overlay.restoration is not None, overlay.status.get()
        assert Path(overlay.path) == source
        assert app.restoration_window.winfo_exists()
        app.open_restoration_overlay()
        assert app.restoration_app is overlay
        assert source.read_bytes() == original
        app.audio_select_none()
        with patch.object(namespace["messagebox"], "showinfo") as info:
            app.open_restoration_overlay()
            info.assert_called_once()
        destination = tmp_path / "restored.wav"
        overlay.mode.set("Off")
        with (
            patch.object(overlay, "show_export_report") as report,
            patch.object(namespace["messagebox"], "askyesno", return_value=True),
            patch("tkinter.filedialog.asksaveasfilename", return_value=str(destination)),
        ):
            super(type(overlay), overlay).export()
            deadline = time.monotonic() + 30
            while not report.called and time.monotonic() < deadline:
                root.update()
                time.sleep(.02)
            report.assert_called_once_with(str(destination))
        assert destination.is_file()
        assert source.read_bytes() == original
        assert [app.audio_paths[key] for key in app.audio_tree.selection()] == [destination]
        overlay.busy = True
        with patch.object(namespace["messagebox"], "showinfo") as info:
            app.close()
            info.assert_called_once()
        assert app.restoration_window.winfo_exists()
        overlay.busy = False
        overlay.close()
        root.update()
        assert root.winfo_exists()
        with (
            patch.object(namespace["restoration_overlay"], "load_app", side_effect=ImportError("missing dependency")),
            patch.object(namespace["messagebox"], "showerror") as error,
        ):
            app.open_restoration_overlay()
            assert "missing dependency" in error.call_args.args[1]
    finally:
        root.destroy()
