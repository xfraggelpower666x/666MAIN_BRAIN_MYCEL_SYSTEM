"""R08 external policy bounded trust, dual-attested rotation, signed revocation events.

No network, disk, key generation, or permanent trust-store mutation. The caller owns
and authenticates immutable trust policy, external sequence floors, and signing keys.
This module cannot establish real-world identities or factual truth.
"""
from __future__ import annotations
import hashlib
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .signed_provenance_r07 import (
    verify_signed_sources, canonical_bytes, _hex, _identifier, _timestamp, ENVELOPE_SCHEMA
)

SCHEMA = '666CURES_R08_ROTATED_TRUST_EVIDENCE_V1'
ROTATION_SCHEMA = '666CURES_R08_DUAL_SIGNED_KEY_ROTATION_V1'
REVOCATION_SCHEMA = '666CURES_R08_SIGNED_REVOCATION_EVENT_V1'
MAX_EVENTS = 128


def _validate_public_key(value, name):
    if not isinstance(value, str): raise ValueError('invalid '+name)
    return _hex(value, 32, name)


def _verify(key_hex, signature_hex, payload, label):
    pub = Ed25519PublicKey.from_public_bytes(_validate_public_key(key_hex,label+' key'))
    sig = _hex(signature_hex,64,label+' signature')
    try: pub.verify(sig,canonical_bytes(payload))
    except (InvalidSignature, ValueError) as exc: raise ValueError(label+' signature verification failed') from exc


def _policy(policy):
    if not isinstance(policy, dict) or set(policy) != {'schema','issuer_id','pinned_keys','authorized_rotations','revocation_authority_keys'}:
        raise ValueError('invalid external trust policy')
    if policy['schema'] != '666CURES_R08_EXTERNAL_TRUST_POLICY_V1':raise ValueError('invalid trust policy schema')
    issuer = _identifier(policy['issuer_id'],'issuer')
    keys=policy['pinned_keys']
    if not isinstance(keys,dict) or not keys or len(keys)>32:raise ValueError('invalid external key inventory')
    for kid,pub in keys.items():_identifier(kid,'pinned key ID');_validate_public_key(pub,'pinned key')
    approvals=policy['authorized_rotations']
    if not isinstance(approvals,dict) or len(approvals)>32:raise ValueError('invalid rotation approvals')
    for rid,digest in approvals.items():_identifier(rid,'rotation approval ID');_hex(digest,32,'rotation approval fingerprint')
    authorities=policy['revocation_authority_keys']
    if not isinstance(authorities,list) or not authorities or len(authorities)>32 or len(set(authorities))!=len(authorities):
        raise ValueError('invalid revocation authorities')
    for key_id in authorities:
        if key_id not in keys:raise ValueError('revocation authority not independently pinned')
    return issuer,keys,approvals,set(authorities)


def _rotation(rotation, issuer, pinned, approvals):
    if rotation is None:return dict(pinned),None
    if not isinstance(rotation,dict) or set(rotation) != {'schema','payload','old_signature_hex','new_signature_hex'}:
        raise ValueError('invalid rotation envelope')
    if rotation['schema'] != ROTATION_SCHEMA:raise ValueError('invalid rotation schema')
    p=rotation['payload']
    if not isinstance(p,dict) or set(p) != {'rotation_id','issuer_id','old_key_id','new_key_id','new_public_key_hex','effective_sequence','observed_at'}:
        raise ValueError('invalid rotation payload')
    rid=_identifier(p['rotation_id'],'rotation ID')
    if p['issuer_id']!=issuer:raise ValueError('cross-issuer rotation')
    old=_identifier(p['old_key_id'],'old key');new=_identifier(p['new_key_id'],'new key')
    if old==new or old not in pinned or new in pinned:raise ValueError('invalid rotation key transition')
    newkey=_validate_public_key(p['new_public_key_hex'],'new public key').hex()
    seq=p['effective_sequence']
    if type(seq) is not int or seq<1:raise ValueError('invalid rotation effective sequence')
    _timestamp(p['observed_at'])
    digest=hashlib.sha256(canonical_bytes(p)).hexdigest()
    if approvals.get(rid)!=digest:raise ValueError('rotation not independently approved')
    _verify(pinned[old],rotation['old_signature_hex'],p,'old rotation')
    _verify(newkey,rotation['new_signature_hex'],p,'new rotation')
    keys=dict(pinned);keys[new]=newkey
    return keys, {'rotation_id':rid,'effective_sequence':seq,'old_key_id':old,'new_key_id':new,
                  'approval_fingerprint_sha256':digest,'dual_signature_verified':True}


def _events(events, pinned, authorities, issuer, external_event_floor):
    if type(external_event_floor) is not int or external_event_floor<0:raise ValueError('external event floor required')
    if not isinstance(events,list) or len(events)>MAX_EVENTS:raise ValueError('invalid revocation events')
    seen=set();last=-1; revoked_keys=set();revoked_docs=set();out=[]
    for event in events:
        if not isinstance(event,dict) or set(event) != {'schema','key_id','signature_hex','payload'} or event['schema']!=REVOCATION_SCHEMA:
            raise ValueError('invalid revocation event')
        key_id=_identifier(event['key_id'],'revocation signer')
        if key_id not in authorities:raise ValueError('untrusted revocation signer')
        p=event['payload']
        if not isinstance(p,dict) or set(p)!={'event_id','issuer_id','sequence','issued_at','subject_type','subject_id','reason'}:
            raise ValueError('invalid revocation event payload')
        event_id=_identifier(p['event_id'],'event ID');subject=_identifier(p['subject_id'],'revoked subject')
        if event_id in seen:raise ValueError('duplicate revocation event')
        if p['issuer_id']!=issuer:raise ValueError('cross-issuer revocation')
        seq=p['sequence']
        if type(seq) is not int or seq<0 or seq<=last:raise ValueError('unordered revocation sequence')
        if p['subject_type'] not in ('DOCUMENT','KEY'):raise ValueError('invalid revocation subject')
        _timestamp(p['issued_at'])
        if not isinstance(p['reason'],str) or not 1<=len(p['reason'])<=256:raise ValueError('invalid revocation reason')
        _verify(pinned[key_id],event['signature_hex'],p,'revocation')
        if p['subject_type']=='KEY':revoked_keys.add(subject)
        else:revoked_docs.add(subject)
        seen.add(event_id);last=seq
        out.append({'event_id':event_id,'sequence':seq,'subject_type':p['subject_type'],'subject_id':subject,
                    'signing_key_id':key_id,'signature_verified':True})
    if events and last<external_event_floor:raise ValueError('stale revocation event stream')
    if not events and external_event_floor>0:raise ValueError('external event floor lacks events')
    return revoked_keys,revoked_docs,out


def verify_rotated_sources(documents, envelope, external_trust_policy, *, minimum_sequence,
                           rotation=None, revocation_events=None, minimum_event_sequence=0):
    """Verify a signed R07 registry under a strictly externally supplied R08 policy.

    No trust-on-first-use. There is no automatic acceptance of a new public key,
    no local persistence of sequence floors, and no inference about real issuer identity.
    Caller MUST store and monotonically update floors after external owner review.
    """
    issuer,pinned,approvals,authorities=_policy(external_trust_policy)
    if type(minimum_sequence) is not int or minimum_sequence<0:raise ValueError('external registry floor required')
    keys,receipt=_rotation(rotation,issuer,pinned,approvals)
    if not isinstance(envelope,dict) or envelope.get('schema')!=ENVELOPE_SCHEMA:raise ValueError('invalid R07 envelope')
    key_id=_identifier(envelope.get('key_id'),'registry signer')
    if key_id not in keys:raise ValueError('untrusted registry signer')
    if receipt:
        if key_id!=receipt['new_key_id']:raise ValueError('rotated registry must use new key')
        sequence=envelope.get('payload',{}).get('sequence')
        if type(sequence) is not int or sequence<receipt['effective_sequence']:
            raise ValueError('registry predates effective rotation')
    revoked_keys,revoked_docs,events=_events([] if revocation_events is None else revocation_events,pinned,authorities,issuer,minimum_event_sequence)
    if key_id in revoked_keys:raise ValueError('signing key revoked')
    result=verify_signed_sources(documents,envelope,{key_id:keys[key_id]},minimum_sequence)
    if any(d['document_id'] in revoked_docs for d in result['documents']):
        raise ValueError('signed revocation excludes document')
    return dict(result, schema=SCHEMA, external_trust_policy='CALLER_PINNED_UNVERIFIED_REAL_WORLD_IDENTITY',
                issuer_claim=issuer, rotation=receipt, revocation_events=events,
                revocation_stream='EXTERNAL_FLOOR_APPLIED',registry_sequence_floor=minimum_sequence,
                current_sequence=result['sequence'], automatic_key_promotion=False,
                external_identity_verified=False, external_truth_verified=False,
                allowed_to_execute=False,autoload=False,foreign_writes=False,mutations=[])
