import unittest, json, hashlib, copy, sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from candidate.signed_provenance_r07 import verify_signed_sources, canonical_bytes,ENVELOPE_SCHEMA,SCHEMA
from candidate.source_registry_r06 import REGISTRY_SCHEMA

def fixture():
 priv=Ed25519PrivateKey.generate()
 pub=priv.public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw).hex()
 text='CLAIM CAUSE A -> B'; digest=hashlib.sha256(text.encode()).hexdigest()
 doc={'document_id':'docA','source_text':text,'observed_at':'2026-11-20T10:00:00Z','source_group':'groupA'}
 reg={'schema':REGISTRY_SCHEMA,'review_status':'EXTERNAL_REVIEW_REQUIRED','entries':[{'document_id':'docA','source_group':'groupA','observed_at':'2026-11-20T10:00:00Z','content_sha256':digest,'provenance_ref':'signed_snapshot','issuer_id':'issuerA'}]}
 rev={'revision_id':'rev1','document_id':'docA','observed_at':'2026-11-20T10:00:00Z','parent_revisions':[],'status':'ACTIVE','content_sha256':digest}
 payload={'registry':reg,'sequence':8,'revisions':[rev],'revocations':[],'issued_at':'2026-11-21T00:00:00Z'}
 def envelope(p):return {'schema':ENVELOPE_SCHEMA,'key_id':'independent_anchor','signature_hex':priv.sign(canonical_bytes(p)).hex(),'payload':p}
 return [doc],payload,envelope,{'independent_anchor':pub}

class TestR07(unittest.TestCase):
 def test_good_signature(self):
  d,p,sign,anchors=fixture();r=verify_signed_sources(d,sign(p),anchors,8);self.assertEqual(r['schema'],SCHEMA);self.assertEqual(r['anti_rollback'],'EXTERNAL_FLOOR_APPLIED')
 def test_unsigned_injected_key_rejected(self):
  d,p,sign,anchors=fixture();self.assertRaises(ValueError,verify_signed_sources,d,sign(p),{'other':next(iter(anchors.values()))})
 def test_mutated_signature_rejected(self):
  d,p,sign,anchors=fixture();e=sign(p);e['signature_hex']='00'*64;self.assertRaises(ValueError,verify_signed_sources,d,e,anchors)
 def test_mutated_content_rejected(self):
  d,p,sign,anchors=fixture();d[0]['source_text']='DENY CAUSE A -> B';self.assertRaises(ValueError,verify_signed_sources,d,sign(p),anchors)
 def test_tampered_registry_after_sign_rejected(self):
  d,p,sign,anchors=fixture();e=sign(p);e['payload']['registry']['entries'][0]['issuer_id']='attacker';self.assertRaises(ValueError,verify_signed_sources,d,e,anchors)
 def test_external_floor_prevents_rollback(self):
  d,p,sign,anchors=fixture();self.assertRaises(ValueError,verify_signed_sources,d,sign(p),anchors,9)
 def test_invalid_freshness_floor(self):
  d,p,sign,anchors=fixture();self.assertRaises(ValueError,verify_signed_sources,d,sign(p),anchors,True)
 def test_absent_floor_reported(self):
  d,p,sign,anchors=fixture();self.assertEqual(verify_signed_sources(d,sign(p),anchors)['anti_rollback'],'NOT_ESTABLISHED')
 def test_signed_revocation_rejected(self):
  d,p,sign,anchors=fixture();p['revocations']=['docA'];self.assertRaises(ValueError,verify_signed_sources,d,sign(p),anchors)
 def test_revoked_revision_rejected(self):
  d,p,sign,anchors=fixture();p['revisions'][0]['status']='REVOKED';self.assertRaises(ValueError,verify_signed_sources,d,sign(p),anchors)
 def test_orphan_revision_rejected(self):
  d,p,sign,anchors=fixture();p['revisions'].append(dict(p['revisions'][0],revision_id='rev2',parent_revisions=['missing']));self.assertRaises(ValueError,verify_signed_sources,d,sign(p),anchors)
 def test_revision_cycle_rejected(self):
  d,p,sign,anchors=fixture();p['revisions'][0]['parent_revisions']=['rev1'];self.assertRaises(ValueError,verify_signed_sources,d,sign(p),anchors)
 def test_fork_preserved(self):
  d,p,sign,anchors=fixture();p['revisions'] += [dict(p['revisions'][0],revision_id='rev2',parent_revisions=['rev1']),dict(p['revisions'][0],revision_id='rev3',parent_revisions=['rev1'])]
  r=verify_signed_sources(d,sign(p),anchors);self.assertEqual(r['revision_graph']['forks']['rev1'],['rev2','rev3'])
 def test_temporal_conflict_preserved(self):
  d,p,sign,anchors=fixture();p['revisions'].append(dict(p['revisions'][0],revision_id='rev2',parent_revisions=['rev1'],status='DISPUTED',observed_at='2026-11-21T10:00:00Z'))
  r=verify_signed_sources(d,sign(p),anchors);self.assertEqual(r['revision_graph']['temporal_status_conflicts'][0]['document_id'],'docA')
 def test_claim_not_truth(self):
  d,p,sign,anchors=fixture();r=verify_signed_sources(d,sign(p),anchors);self.assertFalse(r['external_truth_verified']);self.assertFalse(r['allowed_to_execute']);self.assertEqual(r['trust_anchor_external_identity'],'NOT_VERIFIED_BY_THIS_MODULE')
 def test_noncanonical_nan_rejected(self):
  with self.assertRaises(ValueError):canonical_bytes({'a':float('nan')})
 def test_cross_document_revision_rejected(self):
  d,p,sign,anchors=fixture();p['revisions'] += [dict(p['revisions'][0],revision_id='revB',document_id='docB',parent_revisions=['rev1'])];self.assertRaises(ValueError,verify_signed_sources,d,sign(p),anchors)
 def test_missing_revision_rejected(self):
  d,p,sign,anchors=fixture();p['revisions']=[];self.assertRaises(ValueError,verify_signed_sources,d,sign(p),anchors)
 def test_signed_payload_no_authority(self):
  d,p,sign,anchors=fixture();r=verify_signed_sources(d,sign(p),anchors);self.assertEqual(r['mutations'],[]);self.assertFalse(r['automatic_truth_promotion'])
 def test_signature_unknown_extra_rejected(self):
  d,p,sign,anchors=fixture();e=sign(p);e['new']='key';self.assertRaises(ValueError,verify_signed_sources,d,e,anchors)
 def test_reference_only(self):
  r=json.loads((BASE/'integrations/CLS_REFERENCE_INTERFACE_R07.json').read_text());self.assertFalse(r['allowed_to_execute']);self.assertFalse(r['autoload']);self.assertEqual(r['native_integration'],'PROPOSAL_ONLY_NOT_APPLIED')
if __name__=='__main__':unittest.main()
