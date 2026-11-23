"""666TDI v2.5 R0.5: additive track-local causal relation graph.
Design hypotheses are not audio measurements or automatically promoted rules.
"""
from __future__ import annotations
from . import portable as p

SCHEMA='666TDI_RELATIONAL_GRAPH_V1'
KINDS={'STORY','MOTOR','LOW','MID','HIGH','VOICE','LYRICS','ENERGY','SPACE','ENDING','CARD','SOUND_OBJECT','RENDERER'}
RELATIONS={'CAUSES','CONSTRAINS','SUPPORTS','CONFLICTS','TRANSFORMS','RETURNS_WITH_HISTORY','TRANSLATES_TO'}
class GraphError(ValueError):pass

def paths(track_id):
    if not isinstance(track_id,str) or not track_id or '/' in track_id or '\\' in track_id or '..' in track_id:
        raise GraphError('INVALID_TRACK_ID')
    return p.DATA/'tracks'/f'{track_id}.json',p.DATA/'relations'/f'{track_id}.json'

def blank(track_id):
    return {'schema':SCHEMA,'system_id':p.SYSTEM,'track_id':track_id,'revision':0,'nodes':{},'edges':{},'outcomes':[],'assessments':[]}

def verify(g):
    if g.get('schema')!=SCHEMA or g.get('system_id')!=p.SYSTEM:raise GraphError('FOREIGN_AUTHORITY')
    for key,n in g['nodes'].items():
        if n['id']!=key or n['kind'] not in KINDS:raise GraphError('INVALID_NODE')
    for key,e in g['edges'].items():
        if e['id']!=key or e['from'] not in g['nodes'] or e['to'] not in g['nodes'] or e['relation'] not in RELATIONS:
            raise GraphError('BROKEN_EDGE')
    return True

def read(track_id):
    tp,gp=paths(track_id)
    if not tp.exists():raise GraphError('UNKNOWN_TRACK')
    g=p.load(gp,blank(track_id));verify(g)
    if g['track_id']!=track_id:raise GraphError('TRACK_ID_MISMATCH')
    return g

def save(g):
    verify(g); p.atomic(paths(g['track_id'])[1],g)

def node(track_id,kind,value,reason,origin='CURRENT_TRACK'):
    if kind not in KINDS or not value or not reason or not origin:raise GraphError('NODE_MISSING_PROVENANCE')
    g=read(track_id)
    n={'kind':kind,'value':str(value),'reason':reason,'origin':origin,'status':'CANDIDATE_TRACK_LOCAL'}
    n['id']='n-'+p.sha(n)[:16]
    if n['id'] not in g['nodes']:
        g['nodes'][n['id']]=n;g['revision']+=1;save(g)
    return n

def edge(track_id,src,dst,relation,reason,evidence=None):
    g=read(track_id)
    if src not in g['nodes'] or dst not in g['nodes']:raise GraphError('EDGE_ENDPOINT_MISSING')
    if relation not in RELATIONS or not reason:raise GraphError('EDGE_REASON_REQUIRED')
    x={'from':src,'to':dst,'relation':relation,'reason':reason,'evidence':evidence,'status':'CANDIDATE' if not evidence else 'EVIDENCE_ATTACHED'}
    x['id']='e-'+p.sha(x)[:16]
    if x['id'] not in g['edges']:
        g['edges'][x['id']]=x;g['revision']+=1;save(g)
    return x

def build(track_id):
    t=p.load(paths(track_id)[0]); mapped={}
    fields={'story':'STORY','motor':'MOTOR','mid':'MID','high':'HIGH','voice':'VOICE','lyrics':'LYRICS','energy':'ENERGY','atmosphere':'SPACE','ending':'ENDING'}
    for k,kind in fields.items():
        v=t.get(k)
        if v and isinstance(v,str):mapped[k]=node(track_id,kind,v,'Creator track input: '+k)['id']
    for a,b,relation,why in [('motor','mid','CONSTRAINS','MID respects stable motor timing'),('motor','high','CONSTRAINS','Perceived movement must not destabilize LOW'),('story','energy','CAUSES','Narrative pressure needs structural motivation'),('voice','mid','CONFLICTS','Potential masking conflict: must be listened to'),('energy','ending','CAUSES','Ending should resolve energy promises')]:
        if a in mapped and b in mapped:edge(track_id,mapped[a],mapped[b],relation,why)
    return inspect(track_id)

def inspect(track_id):
    g=read(track_id)
    return {'status':'STRUCTURE_VERIFIED_AUDIO_UNTESTED','track_id':track_id,'revision':g['revision'], 'node_count':len(g['nodes']), 'edge_count':len(g['edges']), 'outcomes':len(g['outcomes']),'audio_verified':False}

def assess(track_id):
    g=read(track_id); kinds={n['kind'] for n in g['nodes'].values()}
    flags=[]
    if 'MOTOR' not in kinds:flags.append('MOTOR_UNSPECIFIED')
    if 'ENDING' not in kinds:flags.append('ENDING_UNSPECIFIED')
    if any(x['relation']=='CONFLICTS' for x in g['edges'].values()):flags.append('POTENTIAL_CONFLICT_REQUIRES_AUDIO')
    return {'status':'DESIGN_REVIEW_NOT_AUDIO_AUDIT','flags':flags,'no_automatic_repairs':True}

def outcome(track_id,renderer,target,observed,evidence_type='USER_REPORTED',artifact=None):
    if evidence_type not in {'USER_REPORTED','HYPOTHESIS','MEASURED_AUDIO','REPEATED_TEST'}:raise GraphError('INVALID_EVIDENCE_TYPE')
    if evidence_type in {'MEASURED_AUDIO','REPEATED_TEST'} and not artifact:raise GraphError('AUDIO_ARTIFACT_REQUIRED')
    if not renderer or not target or not observed:raise GraphError('INCOMPLETE_OUTCOME')
    g=read(track_id)
    x={'renderer':renderer,'target':target,'observed':observed,'evidence_type':evidence_type,'artifact':artifact,'status':'PROVISIONAL','global_rule':False}
    x['id']='o-'+p.sha(x)[:16]
    if x['id'] not in [z['id'] for z in g['outcomes']]:g['outcomes'].append(x);g['revision']+=1;save(g)
    return x

def classify(track_id,outcome_id,cause,evidence=None,reviewer=None):
    causes={'UNKNOWN','DESIGN_FAILURE','TRANSLATION_FAILURE','RENDERER_LIMIT','RANDOM_VARIANCE','EXECUTION_FAILURE'}
    if cause not in causes:raise GraphError('UNKNOWN_CAUSE')
    g=read(track_id)
    if outcome_id not in [x['id'] for x in g['outcomes']]:raise GraphError('UNKNOWN_OUTCOME')
    if cause!='UNKNOWN' and not (evidence and reviewer):raise GraphError('EVIDENCE_AND_REVIEW_REQUIRED')
    x={'outcome_id':outcome_id,'cause':cause,'evidence':evidence,'reviewer':reviewer,'status':'HYPOTHESIS' if cause=='UNKNOWN' else 'SCOPED_REVIEWED','global_rule':False}
    x['id']='a-'+p.sha(x)[:16]
    if x['id'] not in [z['id'] for z in g['assessments']]:g['assessments'].append(x);g['revision']+=1;save(g)
    return x

def rehydrate():
    base=p.rehydrate();problems=list(base['problems']);graphs={}
    directory=p.DATA/'relations'
    if directory.exists():
        for file in sorted(directory.glob('*.json')):
            try:
                g=read(file.stem);graphs[file.stem]=g['revision']
            except (ValueError,KeyError,GraphError) as ex:problems.append('RELATION_GRAPH:'+file.name+':'+str(ex))
    return {'status':'VERIFIZIERT_LOCAL_STRUCTURE' if not problems else 'PARTIAL','problems':problems,'graphs':graphs,'audio_verified':False,'foreign_repository_writes':False}
