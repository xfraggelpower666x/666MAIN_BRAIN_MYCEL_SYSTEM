"""Objektiver WAV -> MP3 Vergleich. Kein psychoakustischer Hör-PASS, kein fremdes MP3-Pair."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
import numpy as np
from scipy.signal import correlate
from scipy.fft import rfft,rfftfreq
wav=Path(os.environ.get('LYVRA_REAL_WAV','/mnt/data/YOU ARE MY EMOTIONAL DYNAMITE [0m00s-5m55s].wav'))
if not wav.is_file():
 print('SKIP: real original WAV not available; no fake A/B results')
 raise SystemExit(0)
ff='ffmpeg';ffprobe='ffprobe'
def run(cmd):
 r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-1500:])
 return r.stdout

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for blk in iter(lambda:f.read(1024*1024),b''):h.update(blk)
 return h.hexdigest()
before=digest(wav)
with tempfile.TemporaryDirectory() as td:
    td=Path(td);mp3=td/'ab_320.mp3'
    start='100';duration='12'
    run([ff,'-hide_banner','-nostdin','-v','error','-ss',start,'-t',duration,'-i',str(wav),
         '-vn','-af','aformat=sample_fmts=fltp,aresample=48000','-ar','48000','-ac','2',
         '-c:a','libmp3lame','-compression_level','0','-b:a','320k',str(mp3)])
    run([ff,'-v','error','-xerror','-i',str(mp3),'-f','null','-'])
    def pcm(args):
        return np.frombuffer(run([ff,'-hide_banner','-nostdin','-v','error',*args,'-ac','2',
                                  '-ar','48000','-f','f32le','-acodec','pcm_f32le','pipe:1']),dtype='<f4').reshape(-1,2)
    original=pcm(['-ss',start,'-t',duration,'-i',str(wav)])
    encoded=pcm(['-i',str(mp3)])
    # MP3 Encoder delay wird durch FFmpeg gapless metadata gewöhnlich berücksichtigt.
    # Alignment mit begrenzter Cross-Correlation zur Messung, nicht als falscher Audio-QC-PASS.
    x=original[:min(len(original),len(encoded)),:].mean(axis=1)
    y=encoded[:min(len(original),len(encoded)),:].mean(axis=1)
    ds=8;head=48000*2
    corr=correlate(y[:head:ds],x[:head:ds],mode='full',method='fft')
    lags=np.arange(-len(x[:head:ds])+1,len(y[:head:ds]))
    lag=int(lags[np.argmax(corr)])*ds
    if lag>=0:a=original[:min(len(original),len(encoded)-lag)];b=encoded[lag:lag+len(a)]
    else:a=original[-lag:][:min(len(original)+lag,len(encoded))];b=encoded[:len(a)]
    # RMS band comparison (not subjective transparency measurement)
    bands=[]
    frames=min(len(a),len(b))//8192
    af=a[:frames*8192].reshape(frames,8192,2).mean(axis=2)
    bf=b[:frames*8192].reshape(frames,8192,2).mean(axis=2)
    speca=abs(rfft(af,axis=1))**2;specb=abs(rfft(bf,axis=1))**2
    hz=rfftfreq(8192,1/48000)
    for lo,hi in ((0,4000),(4000,10000),(10000,16000),(16000,22000)):
        ix=(hz>=lo)&(hz<hi)
        ea=float(speca[:,ix].sum());eb=float(specb[:,ix].sum())
        bands.append({'hz':f'{lo}-{hi}','energy_delta_db':round(10*np.log10((eb+1e-20)/(ea+1e-20)),3)})
    report={'schema':'LYVRA_REAL_WAV_MP3_OBJECTIVE_AB_V1','source_wav':wav.name,
            'source_sha256':before,'source_unmodified':digest(wav)==before,
            'test_segment_seconds':12,'test_segment_from_seconds':100,
            'mp3_bitrate_kbps':320,'sample_rate':48000,'normalization':False,
            'decoded_mp3':'PASS','alignment_lag_samples':lag,
            'signal_error_rms':round(float(np.sqrt(np.mean((a-b)**2))),6),
            'frequency_band_energy_comparison':bands,
            'interpretation':'NUMERIC_DIFFERENCES_ONLY_NOT_PROOF_OF_NO_AUDIBLE_ARTIFACTS',
            'paired_user_bad_mp3':'NOT_AVAILABLE','subjective_listening':'NOT_TESTED'}
    out=Path(__file__).resolve().parents[1]/'TEST_REPORT_v2_36_OBJECTIVE_AB.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    assert report['source_unmodified']
    print('PASS real WAV A/B 12s segment, original unchanged, MP3 decoded; no subjective claim')
    print('band deltas',bands)
