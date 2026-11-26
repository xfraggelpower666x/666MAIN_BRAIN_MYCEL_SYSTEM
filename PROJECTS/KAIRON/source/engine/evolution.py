"""666TDI v2.5 · additive musical and character intelligence.
Die ursprüngliche Runtime bleibt unverändert. Keine GitHub-, Netzwerk- oder Provider-Writes.
"""
from __future__ import annotations
from pathlib import Path
import json, hashlib, os, tempfile, datetime, copy
from . import portable as p

ROOT=p.ROOT
MODULE_VERSION='R0.3-additive'

class EvidenceError(ValueError): pass

def identity():
    info=p.load(ROOT/'registry'/'identity_current.json')
    if info.get('system_id')!=p.SYSTEM or info.get('character',{}).get('pronoun_de')!='er':
        raise EvidenceError('IDENTITY_CONFLICT')
    return info

def add_proposal(module_id, source_id, payload, evidence='HISTORICAL_REFERENCE'):
    identity()
    if evidence not in ('HISTORICAL_REFERENCE','CREATOR_CONFIRMED','MEASURED_AUDIO','EXPERIMENT'):
        raise EvidenceError('UNKNOWN_EVIDENCE')
    reg=p.load(ROOT/'registry'/'additive_modules.json')
    if module_id not in reg['modules']: raise EvidenceError('UNKNOWN_MODULE')
    record={'module_id':module_id,'source_id':source_id,'payload':payload,'evidence':evidence,
            'status':'CANDIDATE','is_current_authority':False,'created_utc':p.utc()}
    record['id']='candidate-'+p.sha(record)[:16]
    ledger=p.load(p.DATA/'addon_proposals.json',{'items':[]})
    ledger['items'].append(record)
    p.atomic(p.DATA/'addon_proposals.json',ledger)
    return record

def pressure_arc(stages=None):
    """Checks a conceptual contrast cycle, not actual loudness from sound."""
    stages=stages or ['BODY_LOCK','LOAD','MICRO_DEVIATION','DECOMPRESSION','IMPACT_RETURN','AFTER_PRESSURE']
    needed=['BODY_LOCK','LOAD','DECOMPRESSION','IMPACT_RETURN']
    return {'status':'STRUCTURAL_MODEL_OK' if all(x in stages for x in needed) and stages.index('DECOMPRESSION')<stages.index('IMPACT_RETURN') else 'PARTIAL',
            'stages':stages,'required':needed,'audio_measured':False}

def predictive_tension(events):
    """Open musical promises must be explicitly paid off or remain openly unresolved."""
    open_ids={}; issues=[]
    for i,e in enumerate(events):
        kind=e.get('type'); key=e.get('anchor')
        if not key: issues.append('MISSING_ANCHOR:'+str(i));continue
        if kind=='EXPECT':
            if key in open_ids:issues.append('DUPLICATE_EXPECTATION:'+key)
            open_ids[key]=i
        elif kind=='RESOLVE':
            if key not in open_ids: issues.append('ORPHAN_RESOLUTION:'+key)
            else:del open_ids[key]
        elif kind not in ('DEVIATE','PARTIAL_RELEASE'):
            issues.append('UNKNOWN_EVENT:'+str(kind))
    issues.extend('UNRESOLVED:'+x for x in sorted(open_ids))
    return {'status':'STRUCTURAL_MODEL_OK' if not issues else 'PARTIAL','issues':issues,'not_audio_verified':True}

def sound_object(source, role, material, emergence, motion, transformation, density_curve, termination):
    fields=locals().copy()
    if any(not v for v in fields.values()): raise EvidenceError('SOUND_OBJECT_INCOMPLETE')
    return {'id':'sound-'+p.sha(fields)[:12],'properties':fields,'is_fixed_preset':False,
            'audio_presence_verified':False,'status':'DESIGN_OBJECT'}

def conflict_candidates(foreground, competing):
    """Candidate interventions, not measured masking diagnosis."""
    return {'foreground':foreground,'competing':competing,'order':[
        'TEMPORAL_SEPARATION','ENVELOPE_SHORTENING','ROLE_EXCHANGE',
        'SPECTRAL_TIMBRE_SHIFT','DEPTH_PLACEMENT'],
        'status':'UNVERIFIED_WITHOUT_STEMS','does_not_modify_audio':True}

def temporal_feedback(track_id, layer, text, context=None, supersedes=None):
    valid=('IMMEDIATE_RESONANCE','SETTLED_REFLECTION','TECHNICAL_EVIDENCE','LATER_REINTERPRETATION','SYNTHESIS')
    if layer not in valid:raise EvidenceError('UNKNOWN_FEEDBACK_LAYER')
    if not (p.DATA/'tracks'/f'{track_id}.json').exists():raise EvidenceError('UNKNOWN_TRACK')
    ledger=p.load(p.DATA/'temporal_feedback.json',{'entries':[]})
    if supersedes:
        old=next((x for x in ledger['entries'] if x['id']==supersedes and x['track_id']==track_id),None)
        if old is None:raise EvidenceError('INVALID_SUPERSESSION_TARGET')
        if not context or context.get('explicit_creator_retraction') is not True:
            raise EvidenceError('SUPERSESSION_REQUIRES_CREATOR_RETRACTION')
    obj={'track_id':track_id,'layer':layer,'text':text,'context':context or {},
         'supersedes':supersedes,'utc':p.utc(),'status':'PROVISIONAL',
         'not_automatically_generalized':True}
    obj['id']='temporal-'+p.sha(obj)[:16];ledger['entries'].append(obj)
    p.atomic(p.DATA/'temporal_feedback.json',ledger)
    p.event('FEEDBACK_RECORDED',{'track_id':track_id,'temporal_feedback':obj['id']})
    return obj

def character_readback():
    identity()
    state=p.load(p.DATA/'character.json',{})
    if not state:
        state={'system_id':p.SYSTEM,'character_name':'666TDI','pronoun_de':'er',
            'traits':{},'preferences':{},'experience':[],'version':'2.5','lineage':'666TDI_LOCAL_ONLY',
            'biological_or_consciousness_claim':False}
    issues=[]
    if state.get('system_id')!=p.SYSTEM or state.get('character_name')!='666TDI' or state.get('pronoun_de')!='er':
        issues.append('CHARACTER_IDENTITY_DRIFT')
    return {'status':'VERIFIZIERT_LOCAL' if not issues else 'PARTIAL','problems':issues,'state':state}

def character_proposal(trait, value, reason, evidence_id):
    if not all((trait,value,reason,evidence_id)):raise EvidenceError('INCOMPLETE_CHARACTER_PROPOSAL')
    return add_proposal('character_continuity','character_history',{
        'trait':trait,'proposed_value':value,'reason':reason,'evidence_id':evidence_id,
        'requires_explicit_review':True})

def aperture_geometry(energy, width, focus, edge, trajectory):
    if not all((energy,width,focus,edge,trajectory)):raise EvidenceError('INCOMPLETE_APERTURE')
    return {'source_energy':energy,'geometry':{'width':width,'focus':focus,'edge':edge,'trajectory':trajectory},
            'motor_protected':True,'not_audio_verified':True,'status':'DESIGN_CANDIDATE'}

def comprehensive_status():
    base=p.rehydrate(); char=character_readback(); reg=p.load(ROOT/'registry'/'additive_modules.json')
    return {'name':identity()['name'],'base':base['status'],'base_revision':base['revision'],
            'character':char['status'],'additive_modules':len(reg['modules']),
            'status':'VERIFIZIERT_LOCAL' if base['status']=='VERIFIZIERT_LOCAL' and char['status']=='VERIFIZIERT_LOCAL' else 'PARTIAL',
            'audio_verified':False,'foreign_repo_write_allowed':False}
