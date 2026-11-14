"""Tests Tk-Event-Dispatch mit echten Dateipfaden, NICHT native Explorer-DnD-Host-Abnahme."""
import pathlib,runpy,tkinter as tk,tempfile
from pathlib import Path
m=runpy.run_path(str(Path(__file__).resolve().parents[1]/'MP3_Manager.pyw'),run_name='drop_test')
root=tk.Tk()
try:
 app=m['App'](root)
 with tempfile.TemporaryDirectory() as t:
  folder=Path(t)/'Track Collection';folder.mkdir()
  wav=folder/'A B (1).wav';wav.write_bytes(b'test')
  # Tk splitlist handles brace-wrapped paths containing spaces.
  class Event:pass
  event=Event();event.data='{'+str(wav)+'}'
  app.audio_drop(event)
  root.update()
  assert app.wav_folder.get()==str(folder)
  assert len(app.audio_tree.selection())==1
  print('PASS synthetic Tk drop dispatch with folder containing spaces; no Windows Explorer test claim')
finally:root.destroy()
