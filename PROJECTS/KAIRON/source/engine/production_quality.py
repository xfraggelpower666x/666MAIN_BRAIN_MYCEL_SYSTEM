"""R20.1: track-local prompt evidence, not audio similarity or autonomous composition."""
import re
import hashlib
from . import motor_intelligence, semantic_guard

# Function witnesses, not exhaustive genre or arrangement prescriptions.
AXES = {
    'beat': ('dry kick','four on the floor','broken kick','syncopated kick','soft kick','hard kick'),
    'bassline': ('rolling 1/16 bass','rolling psybass','offbeat bass','triplet bass','bass rests','pitch modulated bass'),
    'groove': ('straight groove','swing groove','syncopated percussion','rolling groove','rhythmic accents'),
    'instrumentation': ('answers acid','answers vocal rhythm','call and response','mutating timbres','instrumental handoff'),
    'vocals': ('clear vocal','dual vocal','whispered vocal','melodic vocal','spoken vocal'),
    'builds': ('build tension','gradual build','vacuum cut','elastic slingshot','layer withdrawal'),
    'drops': ('explosive return','final thrust','bass release','delayed drop','double drop'),
    'atmosphere': ('stereo orbit','spatial motion','pan movement','near far contrast','spectral motion'),
}
MASTER = {
    'club': ('club-ready master','club ready mastering'),
    'loudness': ('maximum clean loudness','maximum clean perceived loudness'),
    'transients': ('punchy transients','preserved transients'),
    'sub': ('tight mono sub','controlled mono subbass','mono sub'),
    'separation': ('clear spectral and vocal separation','spectral and vocal separation'),
    'dynamics': ('preserved dynamics','preserve dynamics'),
    'clipping': ('no clipping','avoid clipping'),
    'limiting': ('no overcompression','no excessive limiting'),
    'artifacts': ('no digital artifacts','no unwanted digital crackle','no unwanted digital artifacts'),
}

def witnesses(pair, terms, negative=False):
    rows=[]
    for field in ('style','extended'):
        value=pair.get(field,'')
        if not isinstance(value,str): raise ValueError('INVALID_PROMPT_FIELD')
        # Avoid fields cannot establish positive musical functions.
        offset=0
        for line in value.splitlines(keepends=True):
            if not line.lstrip().casefold().startswith('avoid:') or negative:
                for term in terms:
                    for a,b in semantic_guard.occurrences(line,term):
                        rows.append({'field':field,'span':[offset+a,offset+b],'text':line[a:b],'function':term})
            offset+=len(line)
    return rows

def compare(current, previous):
    axes={}
    for axis,terms in AXES.items():
        left,right=witnesses(current,terms),witnesses(previous,terms)
        a,b={x['function'] for x in left},{x['function'] for x in right}
        status='UNKNOWN' if not a or not b else 'SAME' if a==b else 'MIXED' if a&b else 'MEANINGFULLY_DIFFERENT'
        axes[axis]={'status':status,'current':left,'previous':right}
    repeated=all(axes[k]['status']=='SAME' for k in ('beat','bassline','groove'))
    dynamic=any(axes[k]['status']=='MEANINGFULLY_DIFFERENT' for k in ('builds','drops'))
    return {'axes':axes,'repeated_motor':repeated,'dynamic_distinction':dynamic,'status':'HOLD' if repeated and not dynamic else 'REVIEW','audio_verified':False}

def mastering(pair):
    return {field:{key:bool(witnesses({field:pair[field]},terms,key in ('clipping','limiting','artifacts'))) for key,terms in MASTER.items()} for field in ('style','extended')}

def duration(plan):
    if not plan: return {'status':'OPEN','audio_verified':False}
    if not isinstance(plan,dict): raise ValueError('INVALID_DURATION_PLAN')
    bpm,bars,meter=plan.get('bpm'),plan.get('bars'),plan.get('meter')
    if type(bpm) not in (int,float) or not 0<bpm<=400 or type(bars) is not int or not 1<=bars<=2048 or meter!='4/4':
        return {'status':'REVIEW','audio_verified':False}
    start,end=plan.get('start_silence',0),plan.get('end_silence',0)
    if any(type(x) not in (int,float) or not 0<=x<=60 for x in (start,end)): return {'status':'REVIEW','audio_verified':False}
    return {'status':'THEORETICAL','seconds':round(bars*240/bpm+start+end,2),'audio_verified':False}

def assess(fields,intent,context=None):
    context={} if context is None else context
    if not isinstance(context,dict): raise ValueError('INVALID_PRODUCTION_CONTEXT')
    pair={k:fields[k]['text'] for k in ('style','extended')}
    history=context.get('prompt_history',[])
    if not isinstance(history,list): raise ValueError('INVALID_HISTORY')
    comparisons=[]; seen=set()
    for item in reversed(history):
        if not isinstance(item,dict) or not all(isinstance(item.get(k),str) and item[k].strip() for k in pair): continue
        if item.get('system_id','666TDI-001')!='666TDI-001': continue
        key=hashlib.sha256((item['style']+'\0'+item['extended']).encode()).hexdigest()
        if key in seen: continue
        seen.add(key); comparisons.append({'reference_sha256':key,**compare(pair,item)})
        if len(comparisons)==6: break
    motor=motor_intelligence.assess(intent,fields,context.get('dj_plan'))
    master=mastering(pair)
    end=semantic_guard.review(fields,intent)['lyric_relations']
    reasons=[]
    if motor['status']=='HOLD': reasons.append('MOTOR_OR_GENRE_HOLD')
    if not all(all(v.values()) for v in master.values()): reasons.append('MASTERING_REVIEW')
    if any(x['status']=='HOLD' for x in comparisons): reasons.append('REPEATED_MOTOR')
    if end['review_required']: reasons.append('VOCAL_END_REVIEW')
    if not all(f['within_reference_budget'] for f in fields.values()): reasons.append('BUDGET_HOLD')
    return {'revision':'R20.1','status':'HOLD' if reasons else 'CREATOR_REVIEW','reasons':reasons,'history_status':'PARTIAL_REFERENCE' if len(comparisons)<5 else 'REFERENCE_AVAILABLE','reference_count':len(comparisons),'comparisons':comparisons,'mastering':master,'duration':duration(context.get('duration_plan')),'motor':motor,'endguard':end,'audio_verified':False,'production_authorized':False,'no_automatic_rewrite':True}
