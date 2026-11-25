import unittest, json, hashlib, sys, copy
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from candidate.source_registry_r06 import verify_sources,REGISTRY_SCHEMA,SCHEMA

def mkdoc(i, content='CLAIM CAUSE A -> B', date='2026-11-20T10:00:00Z', group=None):
 return {'document_id':i,'source_text':content,'observed_at':date,'source_group':group or i}

def reg(docs):
 return {'schema':REGISTRY_SCHEMA,'review_status':'EXTERNAL_REVIEW_REQUIRED','entries':[
  {'document_id':d['document_id'],'source_group':d['source_group'],'observed_at':d['observed_at'],
   'content_sha256':hashlib.sha256(d['source_text'].encode()).hexdigest(),
   'issuer_id':'owner_review_pending','provenance_ref':'offline_fixture'} for d in docs]}

class TestR06(unittest.TestCase):
 def test_registry_matching(self):
  d=[mkdoc('a')];g=verify_sources(d,reg(d));self.assertEqual(g['schema'],SCHEMA);self.assertTrue(g['source_content_integrity'])
 def test_unverified_authenticity(self):
  d=[mkdoc('a')];g=verify_sources(d,reg(d));self.assertEqual(g['registry_authenticity'],'NOT_VERIFIED_BY_THIS_MODULE');self.assertFalse(g['automatic_truth_promotion'])
 def test_unknown_doc_rejected(self):
  a=[mkdoc('a')];b=[mkdoc('b')]
  with self.assertRaises(ValueError):verify_sources(b,reg(a))
 def test_content_tamper_rejected(self):
  d=[mkdoc('a')];r=reg(d);d[0]['source_text']='DENY CAUSE A -> B'
  with self.assertRaises(ValueError):verify_sources(d,r)
 def test_timestamp_tamper_rejected(self):
  d=[mkdoc('a')];r=reg(d);d[0]['observed_at']='2026-11-22T10:00:00Z'
  with self.assertRaises(ValueError):verify_sources(d,r)
 def test_origin_tamper_rejected(self):
  d=[mkdoc('a')];r=reg(d);d[0]['source_group']='another'
  with self.assertRaises(ValueError):verify_sources(d,r)
 def test_duplicate_registry_rejected(self):
  d=[mkdoc('a')];r=reg(d);r['entries'].append(copy.deepcopy(r['entries'][0]))
  with self.assertRaises(ValueError):verify_sources(d,r)
 def test_registry_spoofing_rejected(self):
  d=[mkdoc('a')];r=reg(d);r['entries'][0]['issuer_id']='bad alias/role'
  with self.assertRaises(ValueError):verify_sources(d,r)
 def test_unexpected_execution_flag_rejected(self):
  d=[mkdoc('a')];d[0]['execute']=True
  with self.assertRaises(ValueError):verify_sources(d,reg(d))
 def test_newer_denial_not_superseding(self):
  d=[mkdoc('a'),mkdoc('b','DENY CAUSE A -> B','2026-11-21T10:00:00Z')];e=verify_sources(d,reg(d))['edges'][0]
  self.assertEqual(e['assessment'],'CONTRADICTED_SOURCE_ASSERTIONS');self.assertEqual(len(e['evidence']),2);self.assertFalse(e['temporal_supersession_applied'])
 def test_same_group_not_independent(self):
  d=[mkdoc('a',group='same'),mkdoc('b',group='same')];e=verify_sources(d,reg(d))['edges'][0]
  self.assertEqual(e['distinct_support_groups'],1)
 def test_ambiguous_text_inert(self):
  d=[mkdoc('a','maybe A caused B?')];self.assertEqual(verify_sources(d,reg(d))['edges'],[])
 def test_injection_inert(self):
  d=[mkdoc('a','__import__("os").system("echo fail")')];self.assertEqual(verify_sources(d,reg(d))['edges'],[])
 def test_unknown_not_upgraded(self):
  d=[mkdoc('a','UNKNOWN CAUSE A -> B'),mkdoc('b','HYPOTHESIS CAUSE A -> B')];g=verify_sources(d,reg(d));self.assertEqual(g['edges'][0]['assessment'],'UNCERTAIN_ONLY')
 def test_direction_and_chain(self):
  d=[mkdoc('a','CLAIM CAUSE A -> B\nCLAIM CAUSE B -> C')];g=verify_sources(d,reg(d));self.assertEqual(len(g['edges']),2);self.assertEqual(g['inferred_causal_edges'],[])
 def test_reference_nonexecution(self):
  v=json.loads((BASE/'integrations/CLS_REFERENCE_INTERFACE_R06.json').read_text());self.assertFalse(v['allowed_to_execute']);self.assertEqual(v['triggers'],[]);self.assertEqual(v['native_integration'],'PROPOSAL_ONLY_NOT_APPLIED')
 def test_json_roundtrip(self):
  d=[mkdoc('a')];g=verify_sources(d,reg(d));self.assertEqual(json.loads(json.dumps(g))['schema'],SCHEMA)
 def test_registry_shape_fail_closed(self):
  d=[mkdoc('a')];r=reg(d);r['approved_by']='source claims itself'
  with self.assertRaises(ValueError):verify_sources(d,r)
 def test_invalid_registry_review_flag(self):
  d=[mkdoc('a')];r=reg(d);r['review_status']='TRUSTED'
  with self.assertRaises(ValueError):verify_sources(d,r)
 def test_reversed_evidence_conflict(self):
  d=[mkdoc('a','CLAIM CAUSE A -> B'),mkdoc('b','DENY CAUSE B -> A')];g=verify_sources(d,reg(d));self.assertEqual(len(g['edges']),2)
if __name__=='__main__':unittest.main()
