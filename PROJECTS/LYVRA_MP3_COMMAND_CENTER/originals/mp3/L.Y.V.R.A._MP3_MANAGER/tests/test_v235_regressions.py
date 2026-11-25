"""Echte Regressionstests: Loudnorm-Guard und fehlertreuer Fortschritt."""
import pathlib,runpy,threading,tempfile,json
from unittest.mock import patch
root=pathlib.Path(__file__).resolve().parents[1]
ns=runpy.run_path(str(root/'MP3_Manager.pyw'),run_name='v235_test')
check=ns['validate_linear_loudnorm_measurement']
base={'input_i':'-17.0','input_tp':'-6.0','input_lra':'6.0', 'input_thresh':'-29.0','target_offset':'0.0'}
assert check(base,-14,-2)['input_i']==-17
for changed in ({'input_tp':'-3.0'},{'input_lra':'13.0'},{'input_i':'-inf'}, {'input_tp':'n/a'}):
 try:check({**base,**changed},-14,-2)
 except RuntimeError:pass
 else:raise AssertionError('Dynamische/ungültige Normalisierung hätte gestoppt werden müssen: '+str(changed))
print('PASS linearer Balanced-Radio-Guard / TP-Limit / LRA / invalid data')

class Var:
 def set(self,x): self.value=x
class Button:
 def configure(self,**kwargs):pass
class Root:
 def after(self,ms,func):func()
class Fake:
 pass
f=Fake();f.root=Root();f.cancel_audio=threading.Event();f.process_lock=threading.Lock();f.active_process=None
for var in ('wav_status','current_file','file_percent','label_file','job_details'):setattr(f,var,Var())
f.wav_button=Button();f.convert_busy=True;f.audio_progress=lambda *a:None
progress=[]
f.progress_update=lambda *args:progress.append(args)
f.run_interruptible=lambda cmd,ev: type('Result',(),{'returncode':1,'stdout':'','stderr':'probe failed'})()
with tempfile.TemporaryDirectory() as temp:
 source=pathlib.Path(temp)/'BROKEN.wav';source.write_bytes(b'invalid input preserved')
 original=source.read_bytes()
 with patch.object(ns['messagebox'],'showinfo',lambda *args:None):
  ns['App'].convert_wavs(f,[source],pathlib.Path(temp)/'out','ffmpeg','ffprobe', (48000,320,'fltp','stereo',False,-14,-2,'maximum',True),ns['DEFAULTS'])
 assert source.read_bytes()==original
 assert not list((pathlib.Path(temp)/'out').glob('*.mp3'))
 assert f.current_file.value.startswith('Mit Fehlern beendet')
 assert '0 erfolgreich, 1 fehlgeschlagen' in f.wav_status.value
 assert progress[-1][3:5]==(1,'Mit Fehlern beendet'),progress[-1]
 print('PASS defekte Quelle unverändert, keine Ausgabe, kein irreführender Erfolg')
