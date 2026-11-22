"""R14 Tray failure must fall back to the desktop window safely."""
from types import SimpleNamespace
from klrw.unified_tray import activate_tray_or_fallback

class Text:
    def __init__(self): self.value = None
    def set(self, value): self.value = value

def test_tray_success_does_not_modify_status():
    view=SimpleNamespace(icon=None, tray_error=None, text=Text(), _start_tray=lambda:None)
    assert activate_tray_or_fallback(view) is True
    assert view.tray_error is None

def test_tray_failure_keeps_desktop_display(capsys):
    def start(): raise RuntimeError('system tray not ready')
    view=SimpleNamespace(icon=None,tray_error=None,text=Text(),_start_tray=start)
    assert activate_tray_or_fallback(view) is False
    assert view.icon is None
    assert 'system tray not ready' in view.tray_error
    assert 'Fensteranzeige' in view.text.value
    assert '[TRAY-WARN]' in capsys.readouterr().err

def test_partial_icon_closed_on_error():
    class Icon:
        stopped = False
        def stop(self): self.stopped=True
    icon=Icon()
    def start(): raise OSError('backend error')
    view=SimpleNamespace(icon=icon,tray_error=None,text=Text(),_start_tray=start)
    assert activate_tray_or_fallback(view) is False
    assert icon.stopped and view.icon is None

def test_batch_logs_tray_exit():
    from pathlib import Path
    text=(Path(__file__).resolve().parents[1]/'START_WINDOWS_MENUE.bat').read_text()
    assert 'TRAY_LAUNCH_LAST.log' in text
    assert 'type "%TRAYLOG%"' in text
    assert 'if not "%TRAYEXIT%"=="0"' in text
