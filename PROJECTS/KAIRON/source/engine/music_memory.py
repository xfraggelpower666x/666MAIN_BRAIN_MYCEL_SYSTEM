"""KAIRON A10: provenance-bound prompt history; no automatic creative rules."""
import hashlib
import json

SYSTEM_ID = '666TDI-001'

def digest(record):
    return hashlib.sha256(json.dumps({k:v for k,v in record.items() if k!='sha256'},sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def history(records, current_track=None):
    """Read-only selection; keep issued prompts distinct from confirmed renders."""
    result=[]; seen=set()
    for r in reversed(records):
        if r.get('system_id')!=SYSTEM_ID or r.get('sha256')!=digest(r):
            raise ValueError('MEMORY_INTEGRITY_OR_SCOPE')
        if r.get('track_id')==current_track or r.get('state')!='ISSUED':
            continue
        if not all(isinstance(r.get(k),str) and r[k].strip() for k in ('style','extended')):
            raise ValueError('INVALID_PROMPT_PAIR')
        key=(r['style'],r['extended'])
        if key in seen: continue
        seen.add(key); result.append(r)
        if len(result)==6: break
    return list(reversed(result))

def relations(feedback, context):
    """Exact declared context only; unknown context never supports reuse."""
    if not context or any(v is None or v=='' or v=='UNKNOWN' for v in context.values()):
        return []
    groups={}
    for r in feedback:
        if r.get('system_id')!=SYSTEM_ID or r.get('sha256')!=digest(r):
            raise ValueError('MEMORY_INTEGRITY_OR_SCOPE')
        if r.get('context')!=context or r.get('creator_confirmed') is not True: continue
        if r.get('rating') not in ('SUCCESS','UNSUCCESSFUL','MIXED'): raise ValueError('INVALID_RATING')
        groups.setdefault(r['decision_id'],[]).append(r)
    out=[]
    for decision, rows in groups.items():
        ratings={r['rating'] for r in rows}
        conflict='SUCCESS' in ratings and 'UNSUCCESSFUL' in ratings
        out.append({'decision_id':decision,'evidence':[r['sha256'] for r in rows], 'ratings':sorted(ratings),'status':'CONTRADICTION_REVIEW' if conflict else 'CONTEXTUAL_CANDIDATE','causal_proof':False,'automatic_promotion':False})
    return out

def audit(records, feedback, context, current_track=None):
    refs=history(records,current_track)
    return {'prompt_history':refs,'relations':relations(feedback,context),'reference_count':len(refs),'audio_verified':False,'production_authorized':False}
