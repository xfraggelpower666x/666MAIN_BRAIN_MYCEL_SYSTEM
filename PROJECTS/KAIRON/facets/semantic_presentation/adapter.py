"""666TDI-001: source-bound presentation evidence adapter (non-composing).

No media generation, renderer invocation, network access or filesystem writes.
Input decisions and copy fields must have been resolved by native 666TDI first.
"""
from __future__ import annotations
from copy import deepcopy

SYSTEM_ID = '666TDI-001'
SCHEMA = '666TDI_SEMANTIC_PRESENTATION_V1'
DEFAULT_ORDER = ('Title', 'Extended', 'Style', 'Lyrics')

class PresentationError(ValueError):
    pass


def utf16_units(value: str) -> int:
    if not isinstance(value, str):
        raise PresentationError('PAYLOAD_NOT_STRING')
    return len(value.encode('utf-16-le')) // 2


def assemble(*, track_id: str, mode: str, decisions: list, fields: dict,
             limits: dict, device_route: dict | None = None,
             forecast: list | None = None, visual: dict | None = None) -> dict:
    """Pure presentation projection; it MUST NOT create musical decisions."""
    if not isinstance(track_id, str) or not track_id or '/' in track_id or '\\' in track_id:
        raise PresentationError('TRACK_ID_INVALID')
    if mode not in ('SOURCE', 'DISCOVERY'):
        raise PresentationError('MODE_UNSUPPORTED')
    if not isinstance(fields, dict) or not isinstance(limits, dict):
        raise PresentationError('INVALID_FIELD_CONTRACT')
    if not isinstance(decisions, list):
        raise PresentationError('DECISIONS_NOT_LIST')
    for name in DEFAULT_ORDER:
        if name not in fields or name not in limits:
            raise PresentationError('MISSING_FIELD_OR_LIMIT:' + name)
    if any(k not in (*DEFAULT_ORDER, 'My Taste') for k in fields):
        raise PresentationError('UNKNOWN_COPY_FIELD')
    if 'My Taste' in fields and 'My Taste' not in limits:
        raise PresentationError('MISSING_MYTASTE_LIMIT')
    order = ('Title', 'Extended') + (('My Taste',) if 'My Taste' in fields else ()) + ('Style', 'Lyrics')
    copy_fields = []
    for name in order:
        value = fields[name]
        count = utf16_units(value)
        max_units = limits[name]
        if type(max_units) is not int or max_units < 1:
            raise PresentationError('INVALID_LIMIT:' + name)
        if count > max_units:
            raise PresentationError('UTF16_LIMIT_EXCEEDED:' + name)
        copy_fields.append({'name': name, 'payload': value, 'utf16_units': count,
                            'max_utf16_units': max_units, 'copy_payload_exact': True})
    relations = []
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            raise PresentationError('DECISION_INVALID')
        if not all(isinstance(decision.get(key), str) and decision[key].strip()
                   for key in ('cause', 'musical_consequence', 'evidence_ref')):
            raise PresentationError('DECISION_PROVENANCE_MISSING:' + str(index))
        relations.append({key: decision[key] for key in ('cause', 'musical_consequence', 'evidence_ref')})
    if device_route is not None and (not isinstance(device_route, dict)
                                     or device_route.get('creator_confirmed') is not True):
        raise PresentationError('DEVICE_ROUTE_NOT_CONFIRMED')
    if forecast is not None and (not isinstance(forecast, list)
                                 or not all(isinstance(item, str) for item in forecast)):
        raise PresentationError('FORECAST_INVALID')
    if visual is not None:
        if not isinstance(visual, dict) or visual.get('decision_evidence_ref') not in {r['evidence_ref'] for r in relations}:
            raise PresentationError('VISUAL_NOT_DECISION_BOUND')
    return {'schema': SCHEMA, 'system_id': SYSTEM_ID, 'track_id': track_id, 'mode': mode,
            'source_decisions_only': True, 'music_authority': SYSTEM_ID,
            'causal_preanalysis': relations, 'visual': deepcopy(visual),
            'copy_fields': copy_fields, 'copy_order': list(order),
            'device_route': deepcopy(device_route), 'device_route_status': 'CREATOR_CONFIRMED' if device_route else 'UNRESOLVED',
            'drift_forecast': deepcopy(forecast or []), 'drift_is_observed_audio': False,
            'audio_validated': False, 'host_validated': False,
            'clipboard_readback_verified': False, 'foreign_authority': False,
            'new_music_controller': False, 'image_required': False}

