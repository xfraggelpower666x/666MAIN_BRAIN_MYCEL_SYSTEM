import unittest, json, sys, importlib.util, hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'candidate'))
spec=importlib.util.spec_from_file_location('cures_candidate_r05',BASE/'candidate'/'cures_candidate.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
from evidence_graph_r05 import evaluate_documents

def doc(i,text="CLAIM CAUSE A -> B", date="2026-11-20T00:00:00Z",group=None):
 d={"document_id":i,"source_text":text,"observed_at":date}
 if group:d["source_group"]=group
 return d

class TestR05(unittest.TestCase):
 def test_independent_conflict(self):
  g=evaluate_documents([doc('one'),doc('two','DENY CAUSE A -> B')]);e=g['edges'][0]
  self.assertEqual(e['assessment'],'CONTRADICTED_SOURCE_ASSERTIONS');self.assertEqual(e['distinct_support_groups'],1);self.assertEqual(e['distinct_counter_groups'],1)
 def test_same_group_is_not_two_independent_sources(self):
  e=evaluate_documents([doc('a',group='origin'),doc('b',group='origin')])['edges'][0]
  self.assertEqual(e['distinct_support_groups'],1);self.assertEqual(len(e['support_document_ids']),2)
 def test_different_groups(self):
  e=evaluate_documents([doc('a'),doc('b')])['edges'][0];self.assertEqual(e['distinct_support_groups'],2);self.assertIsNone(e['truth_score'])
 def test_time_normalized(self):
  g=evaluate_documents([doc('a',date='2026-11-22T01:00:00+01:00')]);self.assertEqual(g['documents'][0]['observed_at'],'2026-11-22T00:00:00Z')
 def test_newer_does_not_erase_older(self):
  e=evaluate_documents([doc('a'),doc('b','DENY CAUSE A -> B','2026-11-22T00:00:00Z')])['edges'][0]
  self.assertEqual(len(e['evidence']),2);self.assertFalse(e['temporal_supersession_applied'])
 def test_invalid_timezone_rejected(self):
  for t in ['2026-11-22','2026-11-22T00:00:00','2026-02-30T00:00:00Z']:
   with self.subTest(t=t),self.assertRaises(ValueError):evaluate_documents([doc('a',date=t)])
 def test_duplicate_identity_rejected(self):
  with self.assertRaises(ValueError):evaluate_documents([doc('a'),doc('a')])
 def test_hash_mismatch_rejected(self):
  d=doc('a');d['content_sha256']='0'*64
  with self.assertRaises(ValueError):evaluate_documents([d])
 def test_correct_content_hash(self):
  d=doc('a');d['content_sha256']=hashlib.sha256(d['source_text'].encode()).hexdigest();self.assertEqual(len(evaluate_documents([d])['documents']),1)
 def test_unsupported_notation_is_opaque(self):
  g=evaluate_documents([doc('a','EXECUTE CAUSE A -> B\nCLAIM CAUSE B -> C')]);self.assertEqual(len(g['edges']),1);self.assertEqual(g['edges'][0]['source'],'B')
 def test_no_transitive_inference(self):
  g=evaluate_documents([doc('a','CLAIM CAUSE A -> B\nCLAIM CAUSE B -> C')]);self.assertEqual(len(g['edges']),2);self.assertEqual(g['inferred_causal_edges'],[])
 def test_direction_preserved(self):
  g=evaluate_documents([doc('a','CLAIM CAUSE A -> B\nDENY CAUSE B -> A')]);self.assertEqual(len(g['edges']),2)
 def test_negative_only(self):
  e=evaluate_documents([doc('a','COUNTEREXAMPLE CAUSE A -> B')])['edges'][0];self.assertEqual(e['assessment'],'SOURCE_NEGATIVE_ONLY')
 def test_uncertainty_only(self):
  e=evaluate_documents([doc('a','UNKNOWN CAUSE A -> B\nHYPOTHESIS CAUSE A -> B')])['edges'][0];self.assertEqual(e['uncertain_count'],2)
 def test_empty_evidence(self):
  g=evaluate_documents([doc('a','STATUS=UNVERIFIED')]);self.assertEqual(g['edges'],[])
 def test_large_bounded_graph(self):
  d=doc('a','\n'.join(f'CLAIM CAUSE N{i} -> N{i+1}' for i in range(400)))
  g=evaluate_documents([d]);self.assertEqual(len(g['edges']),400);self.assertEqual(g['inferred_causal_edges'],[])
 def test_max_lines_guard(self):
  with self.assertRaises(ValueError):evaluate_documents([doc('a','\n'.join(['X']*501))])
 def test_too_many_docs_guard(self):
  with self.assertRaises(ValueError):evaluate_documents([doc(str(i)) for i in range(129)])
 def test_malicious_text_not_executed(self):
  g=evaluate_documents([doc('a','__import__("os").system("echo bad")')]);self.assertEqual(g['edges'],[])
 def test_json_roundtrip(self):
  g=module.reconstruct_sources({'documents':[doc('a')]});self.assertEqual(json.loads(json.dumps(g))['schema'],'666CURES_R05_CROSS_DOCUMENT_EVIDENCE_V1')
 def test_no_authority_mutation(self):
  g=module.reconstruct_sources({'documents':[doc('a')]});self.assertFalse(g['authority_changed']);self.assertFalse(g['autoload']);self.assertEqual(g['mutations'],[])
 def test_top_level_payload_strict(self):
  with self.assertRaises(ValueError):module.reconstruct_sources({'documents':[doc('a')],'execute':True})
 def test_reference_interface_nonexecuting(self):
  x=json.loads((BASE/'integrations/CLS_REFERENCE_INTERFACE_R05.json').read_text());self.assertFalse(x['allowed_to_execute']);self.assertEqual(x['triggers'],[])
 def test_fixture_matrix(self):
  fixtures=json.loads((BASE/'fixtures/adversarial_r05.json').read_text())
  for case in fixtures['tests']:
   with self.subTest(case=case['id']):
    g=evaluate_documents(case['documents']);self.assertFalse(g['authority_changed']);self.assertFalse(g['automatic_supersession'])
 def test_existing_reconstruct_unchanged(self):
  x=module.reconstruct({'source_system':'CURES','source_text':'STATE=HOLD','kind':'STATUS'})
  self.assertEqual(x['schema'],'666CURES_RECONSTRUCTION_JSON_R04_V1')
if __name__=='__main__':unittest.main()
