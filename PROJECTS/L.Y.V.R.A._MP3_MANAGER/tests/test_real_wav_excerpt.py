"""Reale vom Nutzer bereitgestellte WAV, unveränderte Quelle; nur kurzer temporärer Ausschnitt."""
import pathlib,subprocess,tempfile,runpy,hashlib,threading,json
from unittest.mock import patch
original=pathlib.Path('/mnt/data/YOU ARE MY EMOTIONAL DYNAMITE [0m00s-5m55s].wav')
if not original.is_file():
 print('SKIP: real user WAV not present');raise SystemExit(0)
ns=runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1]/'MP3_Manager.pyw'),run_name='real_wav_test')
class Root:
 def after(self,t,cb):cb()
class Var:
 def set(self,v):pass
class Btn:
 def configure(self,**kw):pass
class Fake: pass
original_hash=ns['file_sha256'](original)
with tempfile.TemporaryDirectory() as tmp:
 td=pathlib.Path(tmp);clip=td/'YOU ARE MY EMOTIONAL DYNAMITE [0m00s-0m08s].wav'
 subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-v','error','-i',str(original),'-t','8','-c:a','pcm_s16le',str(clip)],check=True)
 f=Fake();f.root=Root();f.cancel_audio=threading.Event();f.process_lock=threading.Lock();f.active_process=None
 f.audio_progress=lambda *a:None;f.wav_status=Var();f.wav_button=Btn();f.current_file=Var();f.file_percent=Var();f.label_file=Var();f.job_details=Var();f.convert_busy=True
 f.progress_update=lambda *a:None
 f.run_interruptible=lambda cmd,ev:subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
 with patch.object(ns['messagebox'],'showinfo',lambda *args:None):
  ns['App'].convert_wavs(f,[clip],td/'out','ffmpeg','ffprobe',
      (48000,320,'fltp','stereo',False,-14,-2,'maximum',True),ns['DEFAULTS'])
 target=td/'out'/'YOU ARE MY EMOTIONAL DYNAMITE.mp3'
 assert target.exists(),list((td/'out').iterdir())
 evidence=json.loads((td/'out'/(target.name+'.quality.json')).read_text())
 assert evidence['normalization_applied'] is False and evidence['technical_qc']['decode']=='PASS'
 assert ns['read_tags'](target)['TIT2']=='YOU ARE MY EMOTIONAL DYNAMITE'
 assert ns['file_sha256'](original)==original_hash
 print('PASS: real Suno WAV excerpt encoded, metadata verified, QC decoded')
 print('PASS: no normalization and full source file untouched')
