"""R19.9: additive track-local musical relationship review, not a composer."""
from . import semantic_intelligence as semantic, creative_causal as causal
from .semantic_guard import occurrences

TERMS = {
 'wild': ('directed chaos','wild accents','mutating timbres','wild percussion'),
 'direction': ('shared motif','rhythmic anchor','narrative direction'),
 'oddity': ('unusual accent','unexpected handoff','percussion melody'),
 'currentCause': ('answers vocal rhythm','supports current motif','answers acid'),
 'dissonance': ('artistic dissonance','intentional dissonance'),
 'damage': ('digital clipping','technical damage','unwanted crackle'),
 'genreDrift': ('unrequested genre drift',),
 'lowDamage': ('unstable sub','smeared kick','uncontrolled tempo drift'),
 'unverifiedClaim': ('guaranteed rear localization',),
 'themeLeak': ('prior story copied without approval',),
 'guardFail': ('missing required genre root','missing mastering guard'),
 'emotion': ('grief','hope','defiance','longing','emotional release','trauer','hoffnung','sehnsucht'),
 'dialogue': ('call and response','answers vocal rhythm','answers acid','instrumental handoff','antwortet auf acid','antwortet auf den gesang'),
}
FIELDS = ('story','motor','mid','high','voice','structure','psychoacoustics','energy','atmosphere','ending')

def reference_review(flags):
    if any(flags.get(k) is True for k in ('genreDrift','damage','lowDamage','unverifiedClaim','themeLeak','guardFail')):
        return 'HOLD'
    if ((flags.get('wild') is True and flags.get('direction') is True) or
        (flags.get('oddity') is True and flags.get('currentCause') is True) or flags.get('dissonance') is True or
        (flags.get('perceptual') is True and flags.get('lowStable') is True)):
        return 'CANDIDATE'
    return 'REVIEW'

def derive(intent, sem, ca):
    if not isinstance(intent,dict) or intent.get('system_id','666TDI-001') != '666TDI-001':
        raise ValueError('INVALID_OR_FOREIGN_INTENT')
    if any(r.get("system_id") != "666TDI-001" for r in (sem, ca)):
        raise ValueError("FOREIGN_ANALYSIS_NOT_ALLOWED")
    evidence={}
    for key,terms in TERMS.items():
        rows=[]
        for field in FIELDS:
            value=intent.get(field)
            if not isinstance(value,str): continue
            for term in terms:
                for a,b in occurrences(value,term):
                    rows.append({'field':field,'span':[a,b],'text':value[a:b]})
        if rows: evidence[key]=rows
    # Positive uncontradicted functions only. Titles and sung lyrics do not establish physical motor facts.
    active={}
    for f in sem['functions']:
        if f['status']=='SUPPORTED':
            rows=[e for e in f['support_evidence'] if e['field'] in FIELDS]
            if rows: active[f['id']]=rows
    flags={k:True for k in evidence}
    for key,fn in [('lowStable','LOW_ANCHOR'),('perceptual','SPATIAL_MOTION')]:
        if fn in active: flags[key]=True; evidence[key]=active[fn]
    if 'FORWARD_MOTION' in active and 'direction' not in flags:
        flags['direction']=True; evidence['direction']=active['FORWARD_MOTION']
    possibilities=[]
    status=reference_review(flags)
    relations={r['id']:r for r in ca.get('emergences',[]) if r.get('status')=='CREATIVE_EMERGENCE_CANDIDATE' and all(f in active for f in r['functions'])}
    def propose(name,keys,reason,relation=None):
        if all(k in evidence for k in keys) and (relation is None or relation in relations):
            possibilities.append({'id':name,'evidence':{k:evidence[k] for k in keys},'reason':reason,'causal_relation':relations.get(relation),'status':'HOLD' if status=='HOLD' else 'CANDIDATE','creator_review_required':True})
    propose('DIRECTED_CHAOS',('wild','direction'),'Preserve asymmetry while maintaining the declared trajectory.')
    propose('SPECTRAL_MOTION',('perceptual','lowStable'),'Keep the low reference stable while upper layers move.','STABLE_CORE_MOVING_FIELD')
    propose('INSTRUMENTAL_CONVERSATION',('dialogue',),'Review the explicit response relationship; do not prescribe instruments.')
    for relation in ('VOICE_AS_NARRATIVE_ANCHOR','EXPECTATION_PAYOFF','TRANSFORMING_RECURRENCE'):
        if relation in relations:
            propose('EMOTIONAL_RESONANCE',('emotion',),'Connect declared emotion to the evidenced musical relation; no inferred listener reaction.',relation)
    # Emotional and response candidates are reviewable even without wildness.
    if status=='REVIEW' and possibilities:
        status='CANDIDATE'
    return {'system_id':'666TDI-001','revision':'R19.9','status':status,'evidence':evidence,'possibilities':possibilities,'flags':flags,'audio_verified':False,'automatic_promotion':False,'mandatory_sequence':False,'read_only':True}


def assess(intent, total_bars=None):
    """Convenience entry; the existing preanalysis remains the consumer."""
    from . import track_preanalysis
    sem=semantic.assess(intent)
    ca=causal.assess(intent)
    pre=track_preanalysis.assess(intent,sem,ca,total_bars)
    return {**pre['musical_forces'],'semantic':sem,'causal':ca,'preanalysis':pre}
