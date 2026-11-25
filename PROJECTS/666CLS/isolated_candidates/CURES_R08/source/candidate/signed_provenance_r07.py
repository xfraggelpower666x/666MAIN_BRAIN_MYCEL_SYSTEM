"""R07 Ed25519 trust-anchor-based registry verification and revision DAG.

Pure validation (no disk/network writes). Caller MUST inject independently pinned
trust anchors and an external freshness floor. A signature validates key possession
NOT real-world issuer identity, observation accuracy, or causal truth.
"""
from __future__ import annotations
import hashlib, json, re
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .source_registry_r06 import verify_sources
from .evidence_graph_r05 import _identifier, _timestamp, MAX_DOCUMENTS

SCHEMA = '666CURES_R07_SIGNED_PROVENANCE_V1'
ENVELOPE_SCHEMA = '666CURES_R07_SIGNED_REGISTRY_ENVELOPE_V1'
GRAPH_SCHEMA = '666CURES_R07_REVISION_DAG_V1'
MAX_REVISIONS=512
MAX_SIGNED_BYTES=500_000

def canonical_bytes(value):
    if not isinstance(value,dict):raise ValueError('signed payload must be object')
    try: raw=json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
    except (TypeError,ValueError) as exc:raise ValueError('noncanonicalizable payload') from exc
    if len(raw)>MAX_SIGNED_BYTES:raise ValueError('signed payload too large')
    return raw

def _hex(value,size,name):
    if not isinstance(value,str) or len(value)!=size*2 or re.fullmatch('[0-9a-f]{'+str(size*2)+'}',value) is None:
        raise ValueError('invalid '+name)
    return bytes.fromhex(value)

def _revisions(records):
    if not isinstance(records,list) or len(records)>MAX_REVISIONS:raise ValueError('revision bound exceeded')
    versions={}; edges=[]
    for record in records:
        if not isinstance(record,dict) or set(record)!={'revision_id','document_id','observed_at','parent_revisions','status','content_sha256'}:
            raise ValueError('invalid revision shape')
        rid=_identifier(record['revision_id'],'revision_id')
        if rid in versions:raise ValueError('duplicate revision')
        doc=_identifier(record['document_id'],'document_id')
        moment=_timestamp(record['observed_at'])
        digest=_hex(record['content_sha256'],32,'revision content hash').hex()
        status=record['status']
        if status not in ('ACTIVE','REVOKED','SUPERSEDED','DISPUTED'):raise ValueError('invalid revision state')
        parents=record['parent_revisions']
        if not isinstance(parents,list) or len(parents)>32 or len(parents)!=len(set(map(str,parents))):
            raise ValueError('invalid parent revision set')
        for parent in parents:_identifier(parent,'parent revision')
        versions[rid]={'revision_id':rid,'document_id':doc,'observed_at':moment,'content_sha256':digest,'status':status,'parent_revisions':parents}
    for rid,rev in versions.items():
        for parent in rev['parent_revisions']:
            if parent not in versions:raise ValueError('orphan revision')
            if versions[parent]['document_id']!=rev['document_id']:raise ValueError('cross-document revision edge')
            edges.append({'parent':parent,'child':rid})
    active=set();visited=set()
    def visit(rid):
        if rid in active:raise ValueError('revision cycle')
        if rid in visited:return
        active.add(rid)
        for parent in versions[rid]['parent_revisions']:visit(parent)
        active.remove(rid);visited.add(rid)
    for rid in versions:visit(rid)
    children={rid:[] for rid in versions}
    for edge in edges:children[edge['parent']].append(edge['child'])
    forks={rid:sorted(vals) for rid,vals in children.items() if len(vals)>1}
    conflicts={}
    for rid,record in versions.items():
        conflicts.setdefault(record['document_id'],[]).append(record)
    temporal=[]
    for doc,revlist in conflicts.items():
        statuses={r['status'] for r in revlist}
        if len(statuses)>1:
            temporal.append({'document_id':doc,'revisions':sorted(r['revision_id'] for r in revlist),'statuses':sorted(statuses)})
    return {'schema':GRAPH_SCHEMA,'revisions':list(versions.values()),'edges':edges,'forks':forks,'temporal_status_conflicts':temporal,'auto_supersession':False,'automatic_reinstatement':False}

def verify_signed_sources(documents,envelope,trust_anchors,minimum_sequence=None):
    """Anchor must come from a separately authenticated channel, never envelope.

    Freshness floor is external and monotonic; omitted -> rollback unprotected.
    """
    if not isinstance(envelope,dict) or set(envelope)!={'schema','key_id','signature_hex','payload'}:
        raise ValueError('invalid signed envelope')
    if envelope['schema']!=ENVELOPE_SCHEMA:raise ValueError('invalid envelope schema')
    key_id=_identifier(envelope['key_id'],'key id')
    if not isinstance(trust_anchors,dict) or key_id not in trust_anchors:raise ValueError('untrusted signing key')
    pub=_hex(trust_anchors[key_id],32,'trust anchor')
    signature=_hex(envelope['signature_hex'],64,'signature')
    payload=envelope['payload'];raw=canonical_bytes(payload)
    try: Ed25519PublicKey.from_public_bytes(pub).verify(signature,raw)
    except (InvalidSignature,ValueError) as exc:raise ValueError('signature verification failed') from exc
    if set(payload)!={'registry','sequence','revisions','revocations','issued_at'}:raise ValueError('signed payload fields mismatch')
    seq=payload['sequence']
    if type(seq) is not int or seq<0:raise ValueError('invalid sequence')
    if minimum_sequence is not None and (type(minimum_sequence) is not int or minimum_sequence<0):raise ValueError('invalid external freshness floor')
    if minimum_sequence is not None and seq<minimum_sequence:raise ValueError('signed registry rollback')
    issued=_timestamp(payload['issued_at'])
    registry=payload['registry']
    graph=verify_sources(documents,registry)
    revisions=_revisions(payload['revisions'])
    revocations=payload['revocations']
    if not isinstance(revocations,list) or len(revocations)>MAX_DOCUMENTS or len(revocations)!=len(set(map(str,revocations))):
        raise ValueError('invalid revocations')
    registered=set(d['document_id'] for d in graph['documents'])
    for doc_id in revocations:_identifier(doc_id,'revoked document ID')
    revision_by_doc={}
    for rev in revisions['revisions']:
        revision_by_doc.setdefault(rev['document_id'],[]).append(rev)
    for document in graph['documents']:
        doc=document['document_id']
        doc_revs=revision_by_doc.get(doc,[])
        if not doc_revs: raise ValueError('missing signed revision lineage')
        if not any(r['content_sha256']==document['content_sha256'] for r in doc_revs):
            raise ValueError('document content absent from signed revision history')
        if doc in revocations or any(r['status']=='REVOKED' and r['content_sha256']==document['content_sha256'] for r in doc_revs):
            raise ValueError('revoked document not eligible for evaluation')
        doc_statuses={r['status'] for r in doc_revs if r['content_sha256']==document['content_sha256']}
        if 'ACTIVE' not in doc_statuses:raise ValueError('no active signed revision for document')
    graph.update({'schema':SCHEMA,'signed_registry':'ED25519_SIGNATURE_VERIFIED',
                  'trust_anchor_key_id':key_id,'trust_anchor_fingerprint_sha256':hashlib.sha256(pub).hexdigest(),
                  'trust_anchor_external_identity':'NOT_VERIFIED_BY_THIS_MODULE',
                  'signature_issuer_identity':'REQUIRES_OUT_OF_BAND_ATTESTATION',
                  'sequence':seq,'issued_at':issued,
                  'anti_rollback':'EXTERNAL_FLOOR_APPLIED' if minimum_sequence is not None else 'NOT_ESTABLISHED',
                  'revision_graph':revisions,'revocations':sorted(revocations),
                  'cryptographically_authenticated_registry':True,
                  'external_truth_verified':False,'automatic_truth_promotion':False,
                  'allowed_to_execute':False,'external_io':False,'autoload':False,'mutations':[]})
    return graph
