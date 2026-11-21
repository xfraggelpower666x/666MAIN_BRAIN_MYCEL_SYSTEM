"""666TDI v2.5 R0.6: read-only heritage compatibility. No foreign code execution."""
from __future__ import annotations
from pathlib import Path
import json,hashlib,unicodedata
ROOT=Path(__file__).resolve().parents[1]
class AdapterError(ValueError): pass

def intake_registry():
    records=json.loads((ROOT/'registry'/'r06_intake_inventory.json').read_text(encoding='utf-8'))
    if len(records)!=8 or len(set(x['source_id'] for x in records))!=8:
        raise AdapterError('INVENTORY_INCONSISTENT')
    for item in records:
        if item['zip_crc']!='PASS' or item['unsafe_paths'] or item['repo_write_allowed'] is not False:
            raise AdapterError('SOURCE_QUARANTINE_REQUIRED:'+item['source_id'])
    return records

def candidate_catalog():
    x=json.loads((ROOT/'registry'/'r06_music_candidates.json').read_text(encoding='utf-8'))
    if x['system_id']!='666TDI-001' or x['identity']!='666TDI' or x['character_pronouns']!='er/ihn/ihm':
        raise AdapterError('IDENTITY_VIOLATION')
    if any(i['status']!='HISTORICAL_NON_BINDING_CANDIDATE' for group in ('patterns','presets') for i in x[group]):
        raise AdapterError('UNAUTHORIZED_PROMOTION')
    return x

def match_patterns(words):
    if not isinstance(words,str): raise AdapterError('TEXT_REQUIRED')
    terms={t.lower() for t in words.split()}
    result=[]
    for p in candidate_catalog()['patterns']:
        hits=[f for f in p['characteristics'] if any(token.lower() in terms for token in f.split())]
        if hits:result.append({'source_id':p['source_id'],'matched':hits,'status':'REVIEW_ONLY_NOT_AUTO_APPLIED'})
    return result

def character_count(s,mode='unicode_codepoints'):
    if not isinstance(s,str): raise AdapterError('TEXT_REQUIRED')
    if mode=='unicode_codepoints': return len(s)
    if mode=='utf16_units': return len(s.encode('utf-16-le'))//2
    if mode=='utf8_bytes': return len(s.encode('utf-8'))
    raise AdapterError('UNSUPPORTED_COUNT_MODE')

def field_audit(text,limit,mode='unicode_codepoints'):
    if not isinstance(limit,int) or limit<0:raise AdapterError('INVALID_LIMIT')
    used=character_count(text,mode)
    return {'used':used,'limit':limit,'remaining':limit-used,'fits':used<=limit,'mode':mode,'count_source':'666TDI_LOCAL_IMPLEMENTATION_NOT_EXTERNAL_AUDITOR'}

def ace_step_intake():
    x=next(i for i in intake_registry() if i['source_id']=='ace')
    return {'status':'ADAPTER_REVIEW_ONLY','source_sha256':x['sha256'],'transport':'NO_NETWORK_NO_SERVER_NO_CLOUD_CONSENT','actual_audio_render':False,'integration':'NOT_EXECUTED','backend_capabilities':'REQUIRE_RUNTIME_VERIFICATION'}
