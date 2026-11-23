"""666TDI R0.4: historique references -> local non-authoritative capabilities."""
from __future__ import annotations
import datetime as dt
from . import portable as p
from . import evolution as e

STYLE_FAMILIES={
 'LINE_A':{'meaning':'Dark Full-On / Psytrance propulsion','bpm_reference':144,'signals':('psytrance','forest','full-on','goa','mantra','acid','knatterbass')},
 'LINE_B':{'meaning':'Deep Dark Psytechno / Human-Core / Bunker','bpm_reference':142,'signals':('psytechno','bunker','human','spoken','guitar','cyberpunk','dark techno')},
 'LINE_C':{'meaning':'Afro-Psytrance / Nigerian Pidgin heritage','bpm_reference':None,'signals':('afro','nigerian','pidgin','talking drum','afrobeats','african','yoruba')},
}

def style_context(text, explicit=None):
    """Advisory evidence only; never chooses definitive track design."""
    t=text.casefold()
    evidence={k:[s for s in v['signals'] if s in t] for k,v in STYLE_FAMILIES.items()}
    if explicit is not None and explicit not in STYLE_FAMILIES: raise ValueError('UNKNOWN_FAMILY')
    proposed=explicit if explicit else None
    if not proposed:
        matches=sorted(evidence,key=lambda k:len(evidence[k]),reverse=True)
        if evidence[matches[0]] and len(evidence[matches[0]])>len(evidence[matches[1]]):proposed=matches[0]
    return {'candidate':proposed,'evidence':evidence,'status':'ADVISORY_ONLY',
            'bpm':None,'creator_choice_required_for_fixed_style':True,
            'do_not_erase_source_culture':True,'no_previous_track_clone':True,
            'source_lyric_preservation':True}

def memory_observe(subject, observation, source_id, context='',observed_at=None):
    e.identity()
    if not all((subject,observation,source_id)):raise ValueError('MISSING_EVIDENCE')
    ts=(observed_at or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    record={'subject':subject,'observation':observation,'source_id':source_id,
      'context':context,'observed_at':ts.isoformat(),'status':'PROVISIONAL',
      'promotion':'REQUIRES_REVIEW','system_id':p.SYSTEM}
    record['id']='garden-'+p.sha(record)[:16]
    ledger=p.load(p.DATA/'r04_memory_garden.json',{'entries':[],'schema':'666TDI_MEMORY_GARDEN_V1'})
    if not any(x['id']==record['id'] for x in ledger['entries']):ledger['entries'].append(record)
    p.atomic(p.DATA/'r04_memory_garden.json',ledger)
    p.event('R04_MEMORY_OBSERVATION',{'id':record['id'],'source_id':source_id})
    return record

def memory_review(now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    ledger=p.load(p.DATA/'r04_memory_garden.json',{'entries':[]})
    outcome=[]
    for record in ledger['entries']:
        age=(now-dt.datetime.fromisoformat(record['observed_at'])).total_seconds()/86400
        outcome.append({'id':record['id'],'age_days':round(age,2),
          'decision':'REVIEW_REQUIRED' if age>=7 else 'OBSERVE',
          'automatically_deleted':False,'automatically_promoted':False})
    return {'entries':outcome,'count':len(outcome),'current_authority_unchanged':True}

def role_boundary(requested):
    value=requested.strip().upper()
    modes={'MUSIC_AUTHORING','HTML_CODE_DEV','ANALYTICS_REFERENCE'}
    if value not in modes:raise ValueError('UNKNOWN_MODE')
    return {'mode':value,'scope':'666TDI_LOCAL','separate_mode':True,
      'automatic_cross_mode_activation':False,'foreign_trigger_activation':False}

def character_identity_guard(text):
    state=e.character_readback()
    return {'status':state['status'],'character_name':'666TDI',
      'pronouns_de':['er','ihn','ihm','sein'],
      'historical_text_processed_as_data_only':True,
      'rewritten_historical_quotes':False,
      'identity_source':'LOCAL_666TDI','input_length':len(text)}
