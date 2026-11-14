import tempfile, pathlib, wave, math, struct, runpy, hashlib, threading, subprocess
from unittest.mock import patch
ns=runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1]/'MP3_Manager.pyw'),run_name='qc_test_module')
App=ns['App'];read_tags=ns['read_tags']
class Root:
 def after(self,delay,fn):fn()
class Variable:
 def __init__(self,v=''):self.v=v
 def set(self,v):self.v=v
class Btn:
 def configure(self,**kw):pass
class Fake:
 pass
with tempfile.TemporaryDirectory() as d:
 d=pathlib.Path(d);src=d/'CHAOS (1) [0m00s-0m02s].wav'
 with wave.open(str(src),'wb') as wf:
  wf.setnchannels(2);wf.setsampwidth(2);wf.setframerate(48000)
  samples=(struct.pack('<hh',int(14000*math.sin(i*2*math.pi*250/48000)),int(14000*math.sin(i*2*math.pi*250/48000))) for i in range(96000))
  wf.writeframes(b''.join(samples))
 before=hashlib.sha256(src.read_bytes()).hexdigest()
 f=Fake();f.root=Root();f.cancel_audio=threading.Event();f.process_lock=threading.Lock();f.active_process=None
 f.audio_progress=lambda *a:None;f.wav_status=Variable();f.wav_button=Btn();f.current_file=Variable();f.file_percent=Variable();f.label_file=Variable();f.job_details=Variable();f.convert_busy=True
 f.progress_update=lambda *args:None
 f.run_interruptible=lambda cmd,ev:subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
 f.convert_wavs=lambda *args:App.convert_wavs(f,*args)
 tags={**ns['DEFAULTS'],'TALB':'QUALITY TEST'}
 settings=(48000,320,'fltp','stereo',False,-14,-2,'maximum',True)
 with patch.object(ns['messagebox'],'showinfo',lambda *args:None):
  f.convert_wavs([src],d/'_666MP3_EXPORT','ffmpeg','ffprobe',settings,tags)
 target=d/'_666MP3_EXPORT'/'CHAOS 1.mp3'
 assert target.exists(),list((d/'_666MP3_EXPORT').iterdir())
 read=read_tags(target)
 assert read['TIT2']=='CHAOS 1',read
 for k in ['TPE1','TPE2','TCON','TCOM','TRCK','TPOS','COMM','WOAS']:
  assert read[k]==tags[k],(k,read[k],tags[k])
 assert hashlib.sha256(src.read_bytes()).hexdigest()==before
 assert not list((d/'_666MP3_EXPORT').glob('*.partial.mp3'))
 print('PASS: full conversion -> final name -> ID3 -> complete MP3 decode QC')
 print('PASS: per-track ID3 title = CHAOS 1; all standard metadata and source SHA preserved')
 print('PASS: no temp files left')
