"""KAIRON shared read-only guidance; never dispatches actions."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def guidance(state, root=ROOT):
    menu=json.loads((root/'whole/visual/MENU.json').read_text(encoding='utf-8'))
    contract=json.loads((root/'whole/daemon/CONTRACT.json').read_text(encoding='utf-8'))
    if not isinstance(state,dict): raise ValueError('INVALID_STATE')
    if state.get('system_id')!=contract['system_id']: raise ValueError('FOREIGN_IDENTITY')
    missing=[k for k in contract['required_state'] if k not in state]
    facet=state.get('facet')
    if facet not in contract['adapters']: missing.append('facet_adapter')
    if not state.get('workspace') or not state.get('lineage'): missing.append('context')
    step=state.get('last_verified_step')
    if not isinstance(step,dict) or not step.get('evidence_ref'): missing.append('step_evidence')
    gates=state.get('open_gates')
    if not isinstance(gates,list): missing.append('open_gates_type')
    ready=not missing and not gates
    return {'system_id':contract['system_id'],'name':'KAIRON','status':'GUIDANCE_READY' if ready else 'PARTIAL','missing':missing,'open_gates':gates if isinstance(gates,list) else [],'menu':menu['menu'],'next_action':state.get('next_action') if ready else None,'dispatch_performed':False,'evidence_independently_verified':False}
