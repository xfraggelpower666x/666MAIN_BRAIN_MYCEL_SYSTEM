"""Track-local projection of native causal findings; no new inference authority."""
from copy import deepcopy


def attach(result, report, track_id):
    if (report.get('system_id') != '666TDI-001' or
            report.get('schema') != '666TDI_CREATIVE_CAUSAL_R10_V1' or
            report.get('track_id') != track_id):
        raise ValueError('CAUSAL_SCOPE_MISMATCH')
    accepted, review = [], []
    for item in report.get('emergences', []):
        entry = deepcopy(item)
        if (item.get('status') == 'CREATIVE_EMERGENCE_CANDIDATE'
                and not item.get('constraints') and item.get('evidence')
                and all(item['evidence'].get(k) for k in item.get('functions', []))):
            accepted.append(entry)
        else:
            review.append(entry)
    projection = {'source': report['schema'], 'candidates': accepted,
                  'counterevidence': review, 'collisions': deepcopy(report.get('collisions', [])),
                  'status': 'CREATOR_REVIEW_REQUIRED', 'automatic_promotion': False,
                  'audio_verified': False}
    result['causal_evidence'] = projection
    if result.get('preset_candidate') is not None:
        result['preset_candidate']['causal_evidence'] = deepcopy(projection)
