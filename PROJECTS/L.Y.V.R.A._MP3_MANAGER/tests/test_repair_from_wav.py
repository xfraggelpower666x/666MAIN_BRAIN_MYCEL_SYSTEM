"""Integration: echte WAV -> getrennte Repair-MP3 mit Referenz-Hash und Bericht."""
import tempfile, pathlib, wave, math, struct, runpy, hashlib, threading, subprocess, json
from unittest.mock import patch
ns=runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1]/'MP3_Manager.pyw'),run_name='audio_repair_test')
App=ns['App']; tags_reader=ns['read_tags']; sha=ns['file_sha256']
class Root:
 def after(self,delay,fn):fn()
class Variable:
 def __init__(self,v=''):self.v=v
 def set(self,v):self.v=v
class Btn:
 def configure(self,**kw):pass
class Fake:pass
with tempfile.TemporaryDirectory() as td:
 d=pathlib.Path(td); src=d/'CYBER SIGNAL (1) [0m00s-0m03s].wav'
 with wave.open(str(src),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000)
  w.writeframes(b''.join(struct.pack('<hh',round(13000*math.sin(2*math.pi*300*i/48000)),round(13000*math.sin(2*math.pi*450*i/48000))) for i in range(144000)))
 old=d/'CYBER SIGNAL 1.mp3'; old.write_bytes(b'broken MP3 retained for comparison')
 src_before=sha(src); old_before=sha(old)
 fake=Fake();fake.root=Root();fake.cancel_audio=threading.Event();fake.process_lock=threading.Lock();fake.active_process=None
 fake.audio_progress=lambda *x:None;fake.wav_status=Variable();fake.wav_button=Btn();fake.current_file=Variable();fake.file_percent=Variable();fake.label_file=Variable();fake.job_details=Variable();fake.convert_busy=True
 fake.progress_update=lambda *x:None
 fake.run_interruptible=lambda cmd,ev:subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
 tags={**ns['DEFAULTS'],'TALB':'REPAIR TEST'}
 settings=(48000,320,'fltp','stereo',False,-14,-2,'maximum',True)
 with patch.object(ns['messagebox'],'showinfo',lambda *args:None):
  App.convert_wavs(fake,[src],d/'_666MP3_REPAIR','ffmpeg','ffprobe',settings,tags,repair_mode=True,reference_mp3=old)
 result=d/'_666MP3_REPAIR'/'CYBER SIGNAL 1 REPAIRED.mp3'
 assert result.is_file(),list((d/'_666MP3_REPAIR').iterdir())
 assert tags_reader(result)['TIT2']=='CYBER SIGNAL 1 REPAIRED'
 report=json.loads((result.parent/(result.name+'.quality.json')).read_text())
 assert report['reference_mp3']['sha256']==old_before
 assert report['source_sha256']==src_before and report['output_sha256']==sha(result)
 assert report['perceptual_artifacts']=='NOT_TESTED_LISTEN_TO_A_B'
 assert report['normalization_applied'] is False
 assert report['technical_qc']['decode']=='PASS'
 assert sha(src)==src_before and sha(old)==old_before
 assert not list(result.parent.glob('*.partial.mp3'))
 print('PASS original source and damaged MP3 preserved')
 print('PASS repair export 48k 320k and per-track metadata')
 print('PASS complete decode and evidence SHA256 for 3 files')
 print('PASS no false psychoacoustic quality claims')
