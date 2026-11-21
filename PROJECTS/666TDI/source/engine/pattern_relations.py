"""666TDI v2.5 R0.7 - additive context/evidence-bound historical pattern relations.

This is a transparent rule-based *design assessment*, NOT a claim of audio
understanding, AI semantic comprehension, or validated renderer quality.
Historical candidates never gain creative or execution authority by scoring.
"""
from __future__ import annotations
import copy
import json
import re
from pathlib import Path
from . import portable as p
from . import relational as graph
from .source_adapters import candidate_catalog

SCHEMA = '666TDI_PATTERN_RELATIONS_V1'
# Semantic roles describe functions and effects, NOT fixed prompt words.
# Historical characteristics are interpreted as candidate functions and constraints.
TRAITS = {
  'strong drop': {'goals':['ENERGY','ENDING'], 'needs':['impact','contrast'], 'risks':['unprepared_impact']},
  'minimal vocals': {'goals':['VOICE'], 'needs':['sparse_voice'], 'risks':['narrative_vocal_loss']},
  'loop driven': {'goals':['MOTOR','MID'], 'needs':['recurrent_motion'], 'risks':['static_repetition']},
  'multi-voice': {'goals':['VOICE','LYRICS'], 'needs':['voice_dialogue'], 'risks':['vocal_masking']},
  'instrument layering': {'goals':['MID','HIGH'], 'needs':['layered_arrangement'], 'risks':['frequency_masking']},
  'deep break': {'goals':['ENERGY','SPACE'], 'needs':['contrast'], 'risks':['motor_discontinuity']},
  '3x refrain': {'goals':['LYRICS'], 'needs':['recurrent_hook'], 'risks':['static_repetition']},
  'violin cello piano': {'goals':['MID'], 'needs':['acoustic_timbres'], 'risks':['genre_drift']},
  'voice variation': {'goals':['VOICE'], 'needs':['voice_dialogue'], 'risks':['vocal_identity_drift']},
  'whisper vocals': {'goals':['VOICE'], 'needs':['intimate_voice'], 'risks':['vocal_masking']},
  'slow groove': {'goals':['MOTOR'], 'needs':['relaxed_groove'], 'risks':['motor_discontinuity']},
  'touch language': {'goals':['STORY','LYRICS'], 'needs':['human_intimacy'], 'risks':['unwanted_eroticization']},
  'repetition': {'goals':['LYRICS','MOTOR'], 'needs':['recurrent_motion'], 'risks':['static_repetition']},
  'minimal text': {'goals':['LYRICS'], 'needs':['sparse_voice'], 'risks':['narrative_vocal_loss']},
  'rolling groove': {'goals':['MOTOR'], 'needs':['forward_motion'], 'risks':['motor_discontinuity']},
  'contrast': {'goals':['ENERGY'], 'needs':['contrast'], 'risks':[]},
  'system voice': {'goals':['VOICE'], 'needs':['narrator_voice'], 'risks':['foreign_identity']},
  'build tension': {'goals':['ENERGY'], 'needs':['tension'], 'risks':['unresolved_tension']},
  'intro heavy': {'goals':['ENERGY'], 'needs':['extended_intro'], 'risks':['dj_intro_conflict']},
  'slow build': {'goals':['ENERGY'], 'needs':['tension'], 'risks':['unprepared_impact']},
  'final release': {'goals':['ENDING'], 'needs':['terminal_resolution'], 'risks':['unresolved_tension']},
  'low vocals': {'goals':['VOICE'], 'needs':['sparse_voice'], 'risks':['narrative_vocal_loss']},
  'strong rhythm': {'goals':['MOTOR'], 'needs':['forward_motion'], 'risks':['motor_discontinuity']},
  'clean drop': {'goals':['ENERGY','ENDING'], 'needs':['impact'], 'risks':['unprepared_impact']},
  'build evolution': {'goals':['ENERGY','MID'], 'needs':['tension','transformation'], 'risks':['unresolved_tension']},
  'hard drop': {'goals':['ENERGY'], 'needs':['impact'], 'risks':['unprepared_impact']},
  'dominant voice': {'goals':['VOICE'], 'needs':['foreground_voice'], 'risks':['vocal_masking']},
  'system control': {'goals':['STORY'], 'needs':['machine_narrative'], 'risks':['foreign_identity']},
}
# Small explicit associations are interpretive hypotheses; user should inspect results.
VOCAB = {
 'forward_motion': ('rolling','straight','drive','motor','psy','kick','bass','knatter','treib','vorwärts','rhythm'),
 'contrast': ('contrast','break','drop','release','void','vacuum','wechsel','entlast','kontrast','fake'),
 'impact': ('drop','impact','peak','pressure','druck','hard','hart','final'),
 'recurrent_motion': ('repeat','loop','mantra','refrain','pattern','hook','wiederkehr'),
 'sparse_voice': ('instrumental','minimal vocal','few vocal','no vocal','wenig gesang','sparse'),
 'voice_dialogue': ('dialog','duet','call response','male female','two voices','zweistimm','antwort','stimmen'),
 'layered_arrangement': ('layer','multi','instrument','arrangement','acid','fm','orchestrat','schicht'),
 'recurrent_hook': ('hook','mantra','refrain','chorus','wiederkehr'),
 'intimate_voice': ('whisper','breath','intimate','nah','flüster','spoken','leise'),
 'acoustic_timbres': ('violin','cello','piano','guitar','strings','geige','klavier','gitarre'),
 'human_intimacy': ('touch','skin','human','love','heart','emotion','nähe','liebe','berührung'),
 'tension': ('tension','build','pressure','dark','fear','spannung','druck','steiger'),
 'terminal_resolution': ('ending','final','outro','stop','schluss','ende','landing'),
 'transformation': ('transform','mutation','evol','change','return','entwicklung','wechsel'),
 'relaxed_groove': ('slow groove','lounge','chill','laid back','shuffle','swing'),
 'narrator_voice': ('narrator','command voice','system voice','spoken','ansage'),
 'extended_intro': ('intro','opening','anfang','einleitung'),
 'foreground_voice': ('dominant voice','lead vocal','foreground','vordergrund'),
 'machine_narrative': ('system','machine','cyber','code','control','maschine','kontrolle'),
}
RISK = {
 'motor_discontinuity': ('straight','rolling','4/4','dj','stabil','continuous','relentless','psy'),
 'static_repetition': ('evol','change','mutat','transform','return with history','entwicklung','variation','anti loop'),
 'vocal_masking': ('voice','vocal','spoken','whisper','dialog','stimme','gesang'),
 'frequency_masking': ('layer','acid','guitar','mid','high','instrument','schicht'),
 'genre_drift': ('psy','dark','bunker','techno','motor'),
 'unresolved_tension': ('final','ending','outro','release','end','schluss'),
 'unprepared_impact': ('drop','impact','build','tension','peak'),
 'narrative_vocal_loss': ('lyrics','story','verse','narrative','lyrik','text','dialog'),
 'foreign_identity': ('666tdi','system voice','lyvra','character','figur'),
 'vocal_identity_drift': ('voice','vocal','persona','stimme'),
 'unwanted_eroticization': ('human','touch','intim','sensual','body','skin'),
 'dj_intro_conflict': ('dj','mix','intro','beatmatch'),
}

class PatternRelationError(ValueError): pass

def _words(text):
    return set(re.findall(r'[\wäöüß]+',str(text).casefold()))

def _contains(text, phrase):
    # Multiword as phrase; single word as whole token/prefix (for de/en stems).
    text=str(text).casefold()
    phrase=phrase.casefold()
    return phrase in text if ' ' in phrase or len(phrase)>7 else any(x.startswith(phrase) for x in _words(text))

def _signals(g, track):
    signals=[]
    for n in g['nodes'].values():
        if n['kind'] in ('STORY','MOTOR','LOW','MID','HIGH','VOICE','LYRICS','ENERGY','SPACE','ENDING'):
            signals.append({'node_id':n['id'],'kind':n['kind'],'content':n['value'],'origin':n['origin']})
    # Fields can be missing graph nodes (e.g. title, genre). Mark those as field signals.
    for k in ('title','genre','structure','psychoacoustics','avoid'):
        v=track.get(k)
        if v: signals.append({'node_id':'field:'+k,'kind':k.upper(),'content':str(v),'origin':'CURRENT_TRACK_FIELD'})
    return signals

def assess(track_id, *, include_presets=False):
    """Read-only, provenance-rich candidate assessment. Does not select/apply a pattern."""
    g=graph.read(track_id)
    track=p.load(graph.paths(track_id)[0]); signals=_signals(g,track)
    catalog=candidate_catalog(); groups=['patterns']+(['presets'] if include_presets else [])
    results=[]
    existing_conflicts=[e for e in g['edges'].values() if e['relation']=='CONFLICTS']
    for group in groups:
        for candidate in catalog[group]:
            traits=candidate.get('characteristics',candidate.get('tags',[]))
            relations=[];conflicts=[];gaps=[]
            for trait in traits:
                spec=TRAITS.get(trait)
                if not spec:
                    gaps.append({'trait':trait,'reason':'NO_SEMANTIC_MAPPING','status':'OPEN'});continue
                for need in spec['needs']:
                    witnesses=[{'ref':s['node_id'],'kind':s['kind'],'origin':s['origin']} for s in signals if any(_contains(s['content'],term) for term in VOCAB.get(need,()))]
                    if witnesses:
                        relations.append({'trait':trait,'need':need,'function':'SUPPORTS','witnesses':witnesses[:5], 'why':'Track source contains an explicit indicator for this musical function'})
                    else:
                        gaps.append({'trait':trait,'need':need,'reason':'NO_TRACK_EVIDENCE_FOR_FUNCTION'})
                for risk in spec['risks']:
                    witnesses=[{'ref':s['node_id'],'kind':s['kind']} for s in signals if any(_contains(s['content'],term) for term in RISK.get(risk,()))]
                    if witnesses:
                        conflicts.append({'trait':trait,'risk':risk,'witnesses':witnesses[:4],'reason':'Potential counterrelation; requires contextual review, not an observed defect'})
            # Graph edges are local contextual warnings, never global evidence.
            for e in existing_conflicts:
                nodes={g['nodes'][e['from']]['kind'],g['nodes'][e['to']]['kind']}
                if any(set(TRAITS.get(t,{}).get('goals',())) & nodes for t in traits):
                    conflicts.append({'risk':'TRACK_GRAPH_EXISTING_CONFLICT','edge_id':e['id'],'reason':e['reason']})
            # Transparent count, not a quality or musical truth metric.
            state='CONTEXT_SUPPORTED_REVIEW_REQUIRED' if relations else 'INSUFFICIENT_CONTEXT'
            if conflicts:state='COUNTERRELATIONS_REQUIRE_REVIEW' if relations else 'INSUFFICIENT_CONTEXT_WITH_RISKS'
            results.append({'candidate_id':candidate['source_id'],'candidate_type':group[:-1],
                'label':candidate['label'],'origin':candidate['provenance'],
                'status':state,'matches':relations,'counterrelations':conflicts,'unresolved':gaps,
                'evidence_class':'TRACK_STRUCTURE_AND_RULE_BASED_HYPOTHESIS',
                'adopted':False,'audio_verified':False,'renderer_verified':False,
                'explanation':'Explicit musical function witnesses and counterrelations; review required before any track-local use'})
    return {'schema':SCHEMA,'system_id':p.SYSTEM,'identity':'666TDI','pronouns':'er/ihn/ihm',
        'track_id':track_id,'graph_revision':g['revision'],'read_only':True,
        'not_auto_applied':True,'global_promotion':False,'results':results}

def attach_reviewed(track_id,candidate_id,reason,reviewer,allowed_functions):
    """Explicit reviewed track-local association only. No catalogue or compiler mutation."""
    if not isinstance(reason,str) or not reason.strip() or not isinstance(reviewer,str) or not reviewer.strip():
        raise PatternRelationError('EXPLICIT_REVIEW_AND_REASON_REQUIRED')
    if not isinstance(allowed_functions,list) or not allowed_functions or not all(isinstance(t,str) and t in VOCAB for t in allowed_functions):
        raise PatternRelationError('VALID_FUNCTION_SCOPE_REQUIRED')
    a=assess(track_id)
    c=next((v for v in a['results'] if v['candidate_id']==candidate_id),None)
    if not c:raise PatternRelationError('UNKNOWN_HISTORICAL_CANDIDATE')
    supported={x['need'] for x in c['matches']}
    if not set(allowed_functions)<=supported:raise PatternRelationError('UNSUPPORTED_FUNCTION_CANNOT_BE_ADOPTED')
    track_node=graph.node(track_id,'CARD','Historical candidate '+candidate_id,
        'Explicit track-local historical pattern review: '+reason,'HISTORICAL_SOURCE:'+c['origin'])
    g=graph.read(track_id)
    for f in allowed_functions:
        r=next(x for x in c['matches'] if x['need']==f)
        ref=r['witnesses'][0]['ref']
        if ref.startswith('field:'):
            # Need actual graph endpoint for field-only witnesses.
            n=graph.node(track_id,'CARD','Track field evidence '+ref,'Track-local field witness; not a new general rule','CURRENT_TRACK_FIELD')
            ref=n['id']
        graph.edge(track_id,track_node['id'],ref,'SUPPORTS',f'Reviewed track-local {f}: {reason}',
            evidence={'reviewer':reviewer,'source':c['origin'],'scope':'TRACK_LOCAL','status':'REVIEWED_HYPOTHESIS'})
    return {'status':'TRACK_LOCAL_REVIEWED_CANDIDATE_NOT_RENDERED','track_id':track_id,
            'candidate_id':candidate_id,'functions':allowed_functions,'reviewer':reviewer,
            'graph_revision':graph.inspect(track_id)['revision'],'global_rule':False,'audio_verified':False}
