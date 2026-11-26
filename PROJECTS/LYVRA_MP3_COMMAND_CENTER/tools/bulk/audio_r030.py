"""R03.0: synthetische Audio-Abnahme über unveränderte Originaladapter."""
import hashlib,json,os,sys,tempfile,subprocess,wave,math,struct
from pathlib import Path
root=Path(__file__).resolve().parents[2]
orig=root/'originals'
def invoke(script,payload,args=()):
    p=subprocess.run([sys.executable,str(script),*args],input=json.dumps(payload)+'\n',text=True,capture_output=True,timeout=180)
    if p.returncode: raise RuntimeError(p.stdout[-2000:]+p.stderr[-2000:])
    return p.stdout
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    gate=sys.argv[1]
    with tempfile.TemporaryDirectory() as d:
        d=Path(d); src=d/'tone.wav'
        with wave.open(str(src),'wb') as w:
            w.setparams((2,2,44100,0,'NONE','not compressed'))
            w.writeframes(b''.join(struct.pack('<hh',v,v) for i in range(44100*3) for v in [int(5000*math.sin(i*2*math.pi*440/44100))]))
        before=hashfile(src)
        if gate=='dsp':
            import pywt, numpy as np, soundfile as sf
            # Offline DSP requires no PortAudio device or PulseAudio server.
            from importlib.metadata import version
            print(json.dumps(dict(gate='offline_dependencies',pywavelets=pywt.__version__,sounddevice_installed=version('sounddevice'),physical_audio='NOT_TESTED')))
            dry,sr=sf.read(src,always_2d=True)
            outputs={}
            for mode in ('STFT','Wavelet','Both'):
                dest=d/(mode+'.wav')
                invoke(root/'tools/restore_worker.py',dict(source=str(src),destination=str(dest),mode=mode,engine=str(orig/'restore/Restoration-Lab-main')))
                assert dest.stat().st_size>44
                wet,rate=sf.read(dest,always_2d=True)
                assert rate==sr and wet.shape==dry.shape and np.isfinite(wet).all()
                assert np.max(np.abs(wet))>0 and not np.array_equal(wet,dry)
                outputs[mode]=hashfile(dest)
                print(json.dumps(dict(gate='offline_dsp_mode',mode=mode,commit=os.environ.get('GITHUB_SHA'),status='PASS',frames=len(wet),channels=wet.shape[1],sample_rate=rate,sha256=outputs[mode])))
            assert len(set(outputs.values()))==3
        elif gate=='adapters':
            dest=d/'export.mp3'
            bridge=orig/'mp3/ELECTRON_CANDIDATE/engine_bridge.py'
            invoke(bridge,dict(action='export',source=str(src),destination=str(dest),stream=0))
            assert dest.stat().st_size>0
            invoke(bridge,dict(action='inspect',source=str(dest)))
            out=d/'dj';out.mkdir()
            invoke(orig/'dj/666_AUTO_DJ_STUDIO/engine/worker.py',dict(files=[str(dest)],output=str(out),profile='stream',bitrate=256,export_m3u=True))
            assert list(out.glob('*.mp3')) and list(out.glob('*.m3u'))
        else:raise ValueError(gate)
        assert hashfile(src)==before
        print(json.dumps(dict(gate=gate,commit=os.environ.get('GITHUB_SHA'),status='PASS',source_preserved=True)))
if __name__=='__main__':main()
