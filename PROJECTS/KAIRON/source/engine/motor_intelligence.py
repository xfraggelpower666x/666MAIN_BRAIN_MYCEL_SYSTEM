"""R20.0: review literal production fields and declared motor plans, no audio proof."""
import re
from . import semantic_intelligence as semantic
from .semantic_guard import occurrences
ROOT = 'dark psychedelic'
GENRES = {'dark full-on psytrance','dark forest psytrance','twisted dark goa','dark psytrance','dark psytechno','dark industrial psytrance','dark cosmic dub psytrance','dark progressive psytrance','dark goa trance'}

def front(text):
    tokens = [s.strip().casefold() for s in re.split(r'[,;\n]',text)]
    if tokens and re.fullmatch(r'\d+(?:\.\d+)? bpm',tokens[0]): tokens.pop(0)
    if tokens and re.fullmatch(r'[a-g][#b]? (major|minor)',tokens[0]): tokens.pop(0)
    anchors=tokens[:3]
    valid=len(anchors)==3 and anchors[0]==ROOT and len(set(anchors))==3 and all(a in GENRES for a in anchors[1:])
    return {'anchors':anchors,'status':'PASS' if valid else 'HOLD','unknown_genres_require_review':not valid}

def dj_review(plan):
    if not isinstance(plan,dict): raise ValueError('INVALID_MOTOR_PLAN')
    keys=('entryBpm','exitBpm','entryMeter','exitMeter','gridRestored','exitStable')
    if any(k not in plan for k in keys): return 'OPEN'
    for k in ('entryBpm','exitBpm'):
        if type(plan[k]) not in (int,float) or not 0 < plan[k] <= 400: return 'HOLD'
    if any(not isinstance(plan[k],str) or not re.fullmatch(r'[1-9]\d*/(?:1|2|4|8|16|32)',plan[k]) for k in ('entryMeter','exitMeter')): return 'HOLD'
    if any(k in plan and type(plan[k]) is not bool for k in ('gridRestored','exitStable','interiorVariation','explicit')): return 'HOLD'
    return 'PASS' if (plan['entryBpm']==plan['exitBpm'] and plan['entryMeter']==plan['exitMeter'] and plan['gridRestored'] is True and plan['exitStable'] is True and (not plan.get('interiorVariation') or plan.get('explicit') is True)) else 'HOLD'

def reference_review(case):
    if 'style' in case:
        return 'PASS' if all(front(case.get(k,''))['status']=='PASS' for k in ('style','extended')) else 'HOLD'
    return dj_review(case)

LAYER_TERMS={
 'LOW':('mono sub','dry kick','stable sub','kick bass','kick-bass','rolling groove'),
 'LOWER_MID':('rhythmic accents','bass-adjacent support','motor-linked percussion'),
 'UPPER_MID':('mutating timbres','wild accents','answers acid','answers vocal rhythm','dense acid','motif mutation'),
 'HIGH':('stereo orbit','spatial motion','pan movement','apparent acceleration','spectral motion'),
}
FIELDS={'LOW':('motor',),'LOWER_MID':('mid','motor'),'UPPER_MID':('mid','structure'),'HIGH':('high','psychoacoustics')}

def assess(intent, fields, plan=None):
    if intent.get('system_id','666TDI-001')!='666TDI-001': raise ValueError('FOREIGN_INTENT')
    checks={k:front(fields[k]['text']) for k in ('style','extended')}
    layers={}
    for layer,terms in LAYER_TERMS.items():
        ev=[]
        for field in FIELDS[layer]:
            value=intent.get(field) or ''
            if not isinstance(value,str): continue
            for term in terms:
                for a,b in occurrences(value,term): ev.append({'field':field,'span':[a,b],'text':value[a:b]})
        layers[layer]={'evidence':ev,'status':'DECLARED' if ev else 'UNSPECIFIED'}
    # R09 function constraints remain authoritative for the low anchor.
    sem=semantic.assess(intent)
    low=next((f for f in sem['functions'] if f['id']=='LOW_ANCHOR'),{})
    stable=low.get('status')=='SUPPORTED' and any(e['field']=='motor' for e in low.get('support_evidence',[]))
    relations=[]
    if stable and layers['HIGH']['evidence']:
        relations.append({'from':'LOW','to':'HIGH','function':'STABLE_REFERENCE_MOVING_FIELD'})
    if stable and layers['LOWER_MID']['evidence']:
        relations.append({'from':'LOW','to':'LOWER_MID','function':'RHYTHMIC_ORIENTATION'})
    if layers['UPPER_MID']['evidence'] and layers['HIGH']['evidence']:
        relations.append({'from':'UPPER_MID','to':'HIGH','function':'SPECTRAL_INTERACTION_CANDIDATE'})
    dj=dj_review(plan or {})
    prompt_motor={}
    for k in ('style','extended'):
        text=fields[k]['text']
        # Explicit positive cues only; missing language is not a measured defect.
        prompt_motor[k]={'entry_grid':any(occurrences(text,'stable original beatgrid')) or any(occurrences(text,'stable entry grid')),
                         'exit_restore':any(occurrences(text,'restore')) and any(occurrences(text,'dj outro'))}
    budget_ok=all(fields[k].get('within_reference_budget',False) for k in ('style','extended'))
    status='HOLD' if not budget_ok or any(v['status']=='HOLD' for v in checks.values()) or dj=='HOLD' else 'CREATOR_REVIEW'
    return {'revision':'R20.0','status':status,'genre_front':checks,'layers':layers,'relations':relations,'declared_dj_plan':dj,'prompt_motor':prompt_motor,'hardness_from_bpm':False,'bpm':intent.get('bpm'),'audio_verified':False,'dj_sync_verified':False,'production_authorized':False,'no_automatic_rewrite':True,'fixed_frequency_bands':False,'fixed_instruments':False}
