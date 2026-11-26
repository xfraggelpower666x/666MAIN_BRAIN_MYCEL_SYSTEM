"""Portable Trackdesign — eigenständige lokale Runtime, ohne GitHub-Schreibzugriff.
Alle Status- und Lernwerte sind evidenzgebunden; kein Musik-Audio wird hier gerendert.
"""
from __future__ import annotations
import copy, hashlib, json, os, re, tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'runtime'
SYSTEM = '666TDI-001'
VERSION = '2.5.0'
VALID_EVENTS = {'SESSION_STARTED','TRACK_CREATED','INTENT_ANALYZED','CARD_ACTIVATED','COMPILED','FEEDBACK_RECORDED','LEARNING_PROMOTED','HANDOFF_CREATED'}

def utc(): return datetime.now(timezone.utc).isoformat()
def canon(x): return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',',':'))
def sha(x): return hashlib.sha256(canon(x).encode('utf-8')).hexdigest()
def load(p, default=None):
    p=Path(p)
    if not p.exists():
        if default is not None:return copy.deepcopy(default)
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding='utf-8'))
def atomic(p, obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.tmp-',dir=p.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f: f.write(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); f.flush();os.fsync(f.fileno())
        os.replace(name,p)
    finally:
        if os.path.exists(name):os.unlink(name)

def fresh():
    return {'system_id':SYSTEM,'schema':'portable-track-livecircle-v1','version':VERSION,'revision':0,
      'events':[],'active_track_id':None,'track_ids':[],'local_authority':SYSTEM,
      'foreign_repo_write_allowed':False,'created_utc':utc(),'updated_utc':utc()}

def start():
    p=DATA/'livecircle.json'
    if not p.exists(): atomic(p,fresh())
    return rehydrate()

def event(kind, detail):
    if kind not in VALID_EVENTS: raise ValueError('UNKNOWN_EVENT')
    state=load(DATA/'livecircle.json',fresh())
    prev=state['events'][-1]['hash'] if state['events'] else 'GENESIS'
    obj={'seq':len(state['events'])+1,'kind':kind,'utc':utc(),'detail':detail,'prev_hash':prev}
    obj['hash']=sha(obj)
    state['events'].append(obj);state['revision']+=1;state['updated_utc']=utc()
    if kind=='TRACK_CREATED':
        state['active_track_id']=detail['track_id'];state['track_ids'].append(detail['track_id'])
    atomic(DATA/'livecircle.json',state)
    return obj

def rehydrate():
    state=load(DATA/'livecircle.json',fresh())
    problems=[]
    if state.get('system_id')!=SYSTEM:problems.append('SYSTEM_ID_MISMATCH')
    if state.get('foreign_repo_write_allowed') is not False:problems.append('FOREIGN_WRITE_GUARD_MISMATCH')
    last='GENESIS'
    for idx,e in enumerate(state.get('events',[]),1):
        unsigned={k:v for k,v in e.items() if k!='hash'}
        if e.get('seq')!=idx or e.get('prev_hash')!=last or e.get('hash')!=sha(unsigned):
            problems.append(f'EVENT_CHAIN_INVALID:{idx}')
        last=e.get('hash','')
    if state.get('revision')!=len(state.get('events',[])):problems.append('REVISION_EVENT_COUNT_MISMATCH')
    for track_id in state.get('track_ids',[]):
        if not (DATA/'tracks'/f'{track_id}.json').exists(): problems.append('MISSING_TRACK:'+track_id)
    reg=load(ROOT/'registry'/'triggers.json')
    if reg.get('system_id')!=SYSTEM:problems.append('TRIGGER_ID_MISMATCH')
    return {'status':'VERIFIZIERT_LOCAL' if not problems else 'PARTIAL','problems':problems,
            'system_id':SYSTEM,'version':VERSION,'revision':state['revision'],
            'active_track_id':state['active_track_id'],'events_verified':len(state['events'])-len([p for p in problems if p.startswith('EVENT_CHAIN')]),
            'state':state}

def validate_intent(intent):
    for field in ('title','genre','bpm','motor','mid','high','energy'):
        if field not in intent:raise ValueError('MISSING_INTENT:'+field)
    if not 1 <= int(intent['bpm']) <= 350:raise ValueError('INVALID_BPM')

def normalize(intent, track_id=None):
    validate_intent(intent)
    obj=copy.deepcopy(intent)
    obj.setdefault('voice','');obj.setdefault('lyrics','');obj.setdefault('atmosphere','');obj.setdefault('structure','')
    obj.setdefault('psychoacoustics','');obj.setdefault('ending','');obj.setdefault('avoid','')
    obj.setdefault('target_seconds',None);obj.setdefault('story','');obj.setdefault('mode','SOURCE' if obj['lyrics'] else 'DISCOVERY')
    obj.setdefault('references',[])
    obj['track_id']=track_id or 'track-'+sha({'title':obj['title'],'at':utc()})[:12]
    obj['analysis']={'meaning_sources':[],'relations':[],'active_cards':[], 'warnings':[]}
    obj['independent_context']=True
    return obj

def create_track(intent):
    start()
    obj=normalize(intent)
    atomic(DATA/'tracks'/f"{obj['track_id']}.json",obj)
    event('TRACK_CREATED',{'track_id':obj['track_id'],'mode':obj['mode']})
    return obj

# Relation graphs are evidence with contextual edges, never automatic prescriptive triggers.
CARDS=[
 {'id':'motor-straight','kind':'motor','keywords':['psytrance','psy','rolling','motor'],'meaning':'gerichteter kinetischer Antrieb','consequence':'Stabiler 4/4-Kick, klarer 16tel-Psybass, feste DJ-Zeitbasis','anti':['unmotivierter Bounce','unkontrollierter Swing']},
 {'id':'cyber-material','kind':'material','keywords':['machine','circuit','metal','wire','grid','cyber','signal','maschine','metall'],'meaning':'technische Materialität und Reibung','consequence':'Metallische Acid-/FM-Ereignisse und digitale Störtextur','anti':['zufällige Effekte ohne Storybezug']},
 {'id':'somatic-human','kind':'somatic','keywords':['breath','heartbeat','skin','fear','memory','heart','atem','herz','angst'],'meaning':'körperliche Nähe, Verletzlichkeit und Spannung','consequence':'Atemräume, Pulsereignisse, Nähe-/Distanz-Vocals','anti':['automatische Erotisierung']},
 {'id':'psy-orbit','kind':'spatial','keywords':['spiral','portal','orbit','fractal','dimension','echo','psychoacoustic','psychoakustik'],'meaning':'Wahrnehmungsrotation und räumliche Verzerrung','consequence':'Kontrollierte spektrale Bewegung in MID/HIGH bei stabilem LOW','anti':['stereo-unruhiger Subbass']},
 {'id':'memory-return','kind':'story','keywords':['memory','remember','return','echo','erinnerung','zurück'],'meaning':'Rückkehr mit veränderter Bedeutung','consequence':'Hook/Mantra erscheint später transformiert wieder','anti':['mechanisch identischer Refrain']},
 {'id':'dark-pressure','kind':'energy','keywords':['dark','pressure','bunker','industrial','druck','dunkel'],'meaning':'Druck als erzählerische Kraft','consequence':'Kontrast zwischen Kompression, Leerräumen und starken Rückkehrereignissen','anti':['dauerhaft maximale Dichte']},
]

def analyze(track):
    out=copy.deepcopy(track)
    if out.get('mode')=='SOURCE' and not out.get('lyrics') and not out.get('story'):
        out['analysis']['warnings'].append('SOURCE_EMPTY_NO_INVENTION')
    material=' '.join(str(out.get(x,'')) for x in ('title','genre','lyrics','story','motor','mid','high','atmosphere','psychoacoustics')).lower()
    words=set(re.findall(r'[\wäöüß-]+',material,re.UNICODE))
    cards=[]
    for c in CARDS:
        matches=[w for w in c['keywords'] if w in words]
        if matches:
            cards.append({'card_id':c['id'],'kind':c['kind'],'matched_terms':matches,
              'semantic_hypothesis':c['meaning'],'candidate_audible_consequence':c['consequence'],
              'counterrelation':c['anti'],'status':'CANDIDATE_CONTEXT_REVIEW'})
    out['analysis']['active_cards']=cards
    # R0.9: enrich normal analysis with read-only musical-function interpretation.
    from . import semantic_intelligence as semantic
    out['analysis']['semantic_intelligence']=semantic.assess(out)
    from . import creative_causal as causal
    out['analysis']['creative_causal']=causal.assess(out)
    # R20.9: lyric/context Guard-Audit-Trigger is advisory and preserves the native intent.
    from . import context_preset
    out['analysis']['context_preset']=context_preset.evaluate(out)
    out['analysis']['relations']=[{'from':'LOW','to':'MID/HIGH','reason':'Tempo/Phasenstabilität bei wahrnehmungsbezogener Bewegung','constraint':'LOW_STABLE'},
        {'from':'STORY','to':'ARRANGEMENT','reason':'Musikalische Ereignisse müssen eine nachvollziehbare Funktion haben','constraint':'NO_RANDOM_STORY_INVENTION'},
        {'from':'RENDERER','to':'INTENT','reason':'Renderer begrenzt Ausdruck, nicht musikalische Bedeutung','constraint':'NO_COMPOSITION_OVERRIDE'}]
    out['analysis']['meaning_sources']=['current_input','explicit_track_fields']
    if out.get('ending')=='':out['analysis']['warnings'].append('ENDING_NOT_SPECIFIED')
    if out.get('mode')=='SOURCE':out['analysis']['warnings'].append('SOURCE_FIDELITY_REQUIRES_HUMAN_SEMANTIC_REVIEW')
    atomic(DATA/'tracks'/f"{out['track_id']}.json",out)
    event('INTENT_ANALYZED',{'track_id':out['track_id'],'candidate_cards':len(cards)})
    return out

def compiler(track, renderer):
    import sys
    sys.path.insert(0,str(ROOT/'legacy_r01'/'src'))
    from music_arch import MusicalIntent,compile_intent
    fields={k:track.get(k) for k in ('title','genre','bpm','motor','mid','high','atmosphere','energy','voice','lyrics','structure','psychoacoustics','ending','avoid','target_seconds')}
    intent=MusicalIntent(**fields)
    result=compile_intent(intent,renderer)
    result['track_id']=track['track_id'];result['authority']=SYSTEM
    result['graph_context']={'candidate_cards':[c['card_id'] for c in track['analysis']['active_cards']],
       'causal_relations':copy.deepcopy(track['analysis']['relations']),'source_meaning_preserved_in_intent':True}
    result['warnings'].append('NO_REAL_AUDIO_VALIDATION_PERFORMED')
    result['status']='COMPILED_UNVERIFIED_AUDIO' if not result['omissions'] and len(result['warnings'])==1 else 'PARTIAL'
    result['source_intent_sha256']=sha({k:track.get(k) for k in fields})
    atomic(DATA/'compiled'/f"{track['track_id']}--{renderer}.json",result)
    event('COMPILED',{'track_id':track['track_id'],'renderer':renderer,'status':result['status']})
    return result

def record_feedback(track_id,renderer,observation,evidence_type='USER_REPORTED',artifact=None):
    if evidence_type not in {'USER_REPORTED','MEASURED_AUDIO','REPEATED_TEST','HYPOTHESIS'}:raise ValueError('UNKNOWN_EVIDENCE_TYPE')
    if not (DATA/'tracks'/f'{track_id}.json').exists():raise ValueError('UNKNOWN_TRACK')
    ledger=load(DATA/'learning.json',{'observations':[],'promoted':[]})
    x={'id':'obs-'+sha({'track_id':track_id,'observation':observation,'utc':utc()})[:12],
       'track_id':track_id,'renderer':renderer,'observation':observation,
       'evidence_type':evidence_type,'artifact':artifact,'utc':utc(),
       'status':'PROVISIONAL','global_rule':False}
    ledger['observations'].append(x);atomic(DATA/'learning.json',ledger)
    event('FEEDBACK_RECORDED',{'observation_id':x['id'],'track_id':track_id})
    return x

def promotion_gate(observation_ids,reviewer=None):
    ledger=load(DATA/'learning.json',{'observations':[],'promoted':[]})
    items=[x for x in ledger['observations'] if x['id'] in observation_ids]
    reasons=[]
    if len(items)<2 or len(set(x['track_id'] for x in items))<2:reasons.append('REQUIRE_TWO_DISTINCT_TRACKS')
    if any(x['evidence_type'] not in ('MEASURED_AUDIO','REPEATED_TEST') or not x['artifact'] for x in items):reasons.append('REQUIRE_MEASURED_AUDIO_EVIDENCE_AND_ARTIFACT')
    if len(set(x['renderer'] for x in items))!=1:reasons.append('RENDERER_SCOPE_MISMATCH')
    if not reviewer:reasons.append('EXPLICIT_REVIEW_REQUIRED')
    return {'status':'BLOCKIERT' if reasons else 'ELIGIBLE_FOR_SCOPED_PROMOTION','reasons':reasons,'items':len(items),'no_auto_promotion':True}

def handoff():
    r=rehydrate(); x={'schema':'portable-track-handoff-v1','system_id':SYSTEM,'created_utc':utc(),
       'revision':r['revision'],'active_track_id':r['active_track_id'],
       'open_gates':['REAL_AUDIO_VALIDATION','PROVIDER_FIELD_FRESHNESS','CAUSAL_GRAPH_DEEP_SEMANTIC_VALIDATION'],
       'foreign_authority':'REFERENCE_ONLY','next_step':'run controlled renderer A/B test with genuine audio'}
    atomic(DATA/'handoff.json',x);event('HANDOFF_CREATED',{'revision':r['revision']});return x
