"""666TDI v2.5 R0.8: lokale WAV/FLAC-Audio- und Stem-Evidenz. Keine fremden Writes.
Signalheuristiken sind KEINE semantische Klangintelligenz und KEIN Ursachenbeweis.
"""
from __future__ import annotations
from pathlib import Path
from . import portable as p, relational as r
import hashlib, math

# Audio is optional. Core track creation/rehydration must not import numpy.
def _numpy():
    try:
        import numpy as np
    except ImportError as exc:
        raise AudioError('OPTIONAL_AUDIO_DEPENDENCY_MISSING:numpy (pip install numpy soundfile)') from exc
    return np

SCHEMA='666TDI_CAUSAL_AUDIO_FEEDBACK_V1'
class AudioError(ValueError): pass

def _read_audio(path):
    path=Path(path)
    if not path.is_file():raise AudioError('AUDIO_FILE_NOT_FOUND')
    if path.stat().st_size>350*1024*1024:raise AudioError('AUDIO_TOO_LARGE')
    if path.suffix.lower() not in {'.wav','.flac','.aiff','.aif'}:raise AudioError('UNSUPPORTED_LOCAL_AUDIO_FORMAT')
    np=_numpy()
    try:
        import soundfile as sf
    except ImportError as exc:
        raise AudioError('OPTIONAL_AUDIO_DEPENDENCY_MISSING:soundfile (pip install numpy soundfile)') from exc
    try:
        info=sf.info(str(path))
        if not 1<=info.channels<=2 or not 8000<=info.samplerate<=192000:raise AudioError('UNSUPPORTED_CHANNELS_OR_SAMPLE_RATE')
        if info.frames>info.samplerate*1800:raise AudioError('AUDIO_TOO_LONG')
        data,sr=sf.read(str(path),dtype='float32',always_2d=True)
    except (OSError,RuntimeError,ValueError) as exc:raise AudioError('INVALID_AUDIO_FILE') from exc
    if not len(data) or not np.isfinite(data).all():raise AudioError('EMPTY_OR_NONFINITE_AUDIO')
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return data,sr,h.hexdigest()

def measure(path, window_seconds=0.1):
    """Deterministische Pegel-/Spektralmessung ohne trainiertes Wahrnehmungsmodell."""
    np=_numpy()
    data,sr,digest=_read_audio(path)
    channels=data.shape[1]
    mono=data.mean(axis=1,dtype=np.float64)
    absmax=float(np.abs(data).max())
    rms=float(np.sqrt(np.mean(np.square(data.astype(np.float64)))))
    duration=round(len(data)/sr,4)
    step=max(1,int(round(sr*window_seconds)))
    windows=[]
    for start in range(0,len(mono),step):
        chunk=mono[start:start+step]
        if len(chunk)<min(step,64):continue
        v=float(np.sqrt(np.mean(np.square(chunk))))
        windows.append({'start_s':round(start/sr,3),'rms_dbfs':round(20*math.log10(max(v,1e-12)),2)})
    # Frequenzanteile durch fortlaufende 4096er FFT-Blöcke; Energievergleich, kein Masking-Beweis.
    fftsize=4096
    powers=np.zeros(fftsize//2+1,dtype=np.float64)
    blocks=0
    for start in range(0,len(mono)-fftsize+1,fftsize):
        frame=mono[start:start+fftsize]*np.hanning(fftsize)
        powers+=np.abs(np.fft.rfft(frame))**2
        blocks+=1
    freqs=np.fft.rfftfreq(fftsize,1/sr)
    total=float(powers.sum())
    def energy(lo,hi):return round(float(powers[(freqs>=lo)&(freqs<hi)].sum())/total,5) if total>0 else 0.0
    low,mid,high=energy(20,180),energy(180,4000),energy(4000,min(20000,sr/2))
    stereo=None
    if channels==2:
        l,rch=data[:,0].astype(np.float64),data[:,1].astype(np.float64)
        if np.std(l)>1e-10 and np.std(rch)>1e-10:
            stereo=round(float(np.corrcoef(l,rch)[0,1]),4)
    silent=[x for x in windows if x['rms_dbfs']<=-60]
    return {'schema':'666TDI_AUDIO_MEASURE_V1','system_id':p.SYSTEM,'evidence_type':'MEASURED_AUDIO',
      'artifact_sha256':digest,'artifact_size_bytes':Path(path).stat().st_size,
      'filename':Path(path).name,'sample_rate':sr,'channels':channels,'duration_s':duration,
      'sample_peak_dbfs':round(20*math.log10(max(absmax,1e-12)),2),
      'rms_dbfs':round(20*math.log10(max(rms,1e-12)),2),
      'crest_factor_db':round(20*math.log10(max(absmax,1e-12)/max(rms,1e-12)),2),
      'band_energy_ratio':{'low_20_180':low,'mid_180_4000':mid,'high_4000_20000':high},
      'stereo_correlation':stereo,'silence_windows_below_minus60_dbfs':len(silent),
      'rms_windows':windows,'spectral_blocks':blocks,
      'limitations':['PEAK_IS_SAMPLE_PEAK_NOT_TRUE_PEAK','NOT_EBU_R128_LOUDNESS',
       'BAND_ENERGY_NOT_PERCEPTUAL_MASKING','NO_BPM_KEY_OR_VOICE_SEMANTIC_IDENTIFICATION',
       'NO_CAUSAL_ATTRIBUTION_FROM_MEASUREMENT_ALONE']}

def compare(track_id,renderer,audio_path,stem_paths=None,tolerance_seconds=5.0):
    g=r.read(track_id)
    track=p.load(p.DATA/'tracks'/f'{track_id}.json')
    main=measure(audio_path)
    stems={}
    for role,path in (stem_paths or {}).items():
        if not isinstance(role,str) or not role or '/' in role or '\\' in role:raise AudioError('BAD_STEM_ROLE')
        stems[role]=measure(path)
        if abs(stems[role]['duration_s']-main['duration_s'])>1.0:
            raise AudioError('STEM_DURATION_MISMATCH')
    findings=[]
    target=track.get('target_seconds')
    if target is not None:
        try:target=float(target)
        except (ValueError,TypeError):raise AudioError('INVALID_TARGET_DURATION')
        if target<=0:raise AudioError('INVALID_TARGET_DURATION')
        deviation=round(main['duration_s']-target,3)
        findings.append({'feature':'duration','expected_s':target,'observed_s':main['duration_s'],
          'delta_s':deviation,'status':'MEASURED_DEVIATION' if abs(deviation)>tolerance_seconds else 'WITHIN_TOLERANCE',
          'cause':'UNKNOWN'})
    else:findings.append({'feature':'duration','status':'NO_QUANTITATIVE_TARGET','cause':'UNKNOWN'})
    if main['sample_peak_dbfs']>=-0.02:findings.append({'feature':'sample_peak','status':'NEAR_DIGITAL_CEILING',
          'cause':'UNKNOWN','note':'Sample peak near 0 dBFS; clipping not proven'})
    if len(stems)>1:
        # This is only a screening cue; real masking requires temporal spectral and listening analysis.
        roles=list(stems)
        for i,a in enumerate(roles):
            for b in roles[i+1:]:
                ratios=stems[a]['band_energy_ratio'],stems[b]['band_energy_ratio']
                overlap=sum(min(ratios[0][band],ratios[1][band]) for band in ratios[0])
                findings.append({'feature':'stem_spectral_overlap','stem_pair':[a,b],
                  'overlap_screening_index':round(overlap,4),'status':'SCREENING_ONLY',
                  'cause':'UNKNOWN','masking_confirmed':False})
    report={'schema':SCHEMA,'system_id':p.SYSTEM,'track_id':track_id,'renderer':renderer,
        'graph_revision_at_analysis':g['revision'],'track_intent_sha256':p.sha(track),
        'mix':main,'stems':stems,'findings':findings,
        'causal_status':'UNKNOWN_REQUIRES_HUMAN_AND_CONTROLLED_EXPERIMENT',
        'real_audio_measured':True,'renderer_executed_by_666TDI':False,
        'automatic_global_learning':False,'external_repo_write':False}
    report['id']='audio-'+p.sha(report)[:20]
    return report

def record(report):
    if report.get('system_id')!=p.SYSTEM or report.get('schema')!=SCHEMA or not report.get('real_audio_measured'):
        raise AudioError('INVALID_EVIDENCE_REPORT')
    # Audit-Freeze per Content Hash; identical report cannot be silently overwritten.
    fn=p.DATA/'audio_feedback'/f"{report['id']}.json"
    if fn.exists():
        existing=p.load(fn)
        if existing!=report:raise AudioError('EVIDENCE_COLLISION')
        return {'status':'ALREADY_RECORDED','id':report['id']}
    p.atomic(fn,report)
    return {'status':'LOCALLY_RECORDED_PROVISIONAL','id':report['id'],'global_promotion':False}

def review(track_id,report_id,cause,reviewer,evidence_note):
    """Review is scoped; it cannot promote renderer rules or overwrite measurement."""
    valid={'UNKNOWN','DESIGN_FAILURE','TRANSLATION_FAILURE','RENDERER_LIMIT','RANDOM_VARIANCE','EXECUTION_FAILURE'}
    if cause not in valid or not reviewer or not evidence_note:raise AudioError('REVIEW_INCOMPLETE')
    g=r.read(track_id)
    fn=p.DATA/'audio_feedback'/f'{report_id}.json'
    report=p.load(fn)
    if report['track_id']!=track_id or report['id']!=report_id:raise AudioError('TRACK_EVIDENCE_MISMATCH')
    x={'schema':'666TDI_AUDIO_CAUSAL_REVIEW_V1','report_id':report_id,'track_id':track_id,
        'cause_candidate':cause,'reviewer':reviewer,'evidence_note':evidence_note,
        'status':'SCOPED_REVIEW_HYPOTHESIS','global_rule':False}
    x['id']='review-'+p.sha(x)[:20]
    fn=p.DATA/'audio_reviews'/f"{x['id']}.json"
    if fn.exists() and p.load(fn)!=x:raise AudioError('REVIEW_COLLISION')
    p.atomic(fn,x)
    return x

def rehydrate():
    problems=[]
    try:
        for fn in sorted((p.DATA/'audio_feedback').glob('*.json')):
            x=p.load(fn)
            if x.get('schema')!=SCHEMA or x.get('system_id')!=p.SYSTEM or 'audio-'+p.sha({k:v for k,v in x.items() if k!='id'})[:20]!=x.get('id'):
                problems.append('INVALID_AUDIO_REPORT:'+fn.name)
        for fn in sorted((p.DATA/'audio_reviews').glob('*.json')):
            x=p.load(fn)
            if x.get('schema')!='666TDI_AUDIO_CAUSAL_REVIEW_V1' or x.get('global_rule') is not False or 'review-'+p.sha({k:v for k,v in x.items() if k!='id'})[:20]!=x.get('id'):
                problems.append('INVALID_AUDIO_REVIEW:'+fn.name)
    except (ValueError,KeyError,TypeError) as exc:problems.append('AUDIO_EVIDENCE_PARSE:'+str(exc))
    return {'status':'VERIFIZIERT_LOCAL_STRUCTURE' if not problems else 'PARTIAL',
      'problems':problems,'no_global_auto_learning':True}
