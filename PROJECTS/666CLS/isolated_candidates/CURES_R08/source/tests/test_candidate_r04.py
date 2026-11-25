import unittest, importlib.util, sys, json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'candidate'))
spec=importlib.util.spec_from_file_location('cures_candidate_r04',BASE/'candidate'/'cures_candidate.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def run(lines):return mod.reconstruct({'source_system':'TEST','kind':'RELATION','source_text':'\n'.join(lines)})
class GraphR04(unittest.TestCase):
 def test_chain_no_new_edge(self):
  g=run(['CLAIM CAUSE A -> B','CLAIM CAUSE B -> C'])['graph']
  self.assertEqual(len(g['edges']),2);self.assertEqual(g['assertion_paths'][0]['nodes'],['A','B','C']);self.assertEqual(g['new_causal_edges_inferred'],[])
 def test_contradiction(self):
  g=run(['CLAIM CAUSE A -> B','DENY CAUSE A -> B'])['graph']; e=g['edges'][0]
  self.assertEqual(e['assessment'],'CONTRADICTED');self.assertEqual(e['evidence']['support_lines'],[1]);self.assertEqual(e['evidence']['counter_lines'],[2]);self.assertIsNone(e['evidence']['truth_score'])
 def test_counterexample(self):
  e=run(['CLAIM CAUSE A -> B','COUNTEREXAMPLE CAUSE A -> B'])['graph']['edges'][0]
  self.assertEqual(e['evidence']['counter_count'],1)
 def test_hypothesis_is_not_edge(self):
  g=run(['HYPOTHESIS CAUSE A -> B','CLAIM CAUSE B -> C'])['graph'];self.assertFalse(g['assertion_paths'])
 def test_observation_no_causation(self):
  e=run(['OBSERVE CAUSE A -> B'])['graph']['edges'][0]; self.assertEqual(e['assessment'],'UNCONFIRMED_ONLY')
 def test_reverse_direction_separate(self):
  g=run(['CLAIM CAUSE A -> B','DENY CAUSE B -> A'])['graph'];self.assertEqual(len(g['edges']),2)
 def test_status_conflict(self):
  g=run(['STATE=READY','STATE=HOLD'])['graph'];self.assertEqual(g['source_field_conflicts'][0]['assessment'],'CONFLICT_UNRESOLVED')
 def test_unknown_preserved(self):
  g=run(['UNKNOWN CAUSE A -> B'])['graph'];self.assertEqual(g['edges'][0]['evidence']['uncertain_count'],1)
 def test_json_serializable(self):
  data=run(['CLAIM CAUSE A -> B']);self.assertEqual(json.loads(json.dumps(data))['schema'],'666CURES_RECONSTRUCTION_JSON_R04_V1')
 def test_identity_and_no_mutation(self):
  o=run(['CLAIM CAUSE A -> B']);self.assertEqual(o['source_system'],o['preserved_identity']);self.assertFalse(o['authority_changed']);self.assertEqual(o['graph']['mutations'],[])
 def test_cycle_detected_not_proven(self):
  g=run(['CLAIM CAUSE A -> B','CLAIM CAUSE B -> A'])['graph'];self.assertTrue(g['cycles']);self.assertFalse(g['independently_verified'])
 def test_false_fact_not_created(self):
  g=run(['DENY CAUSE A -> B','CLAIM CAUSE B -> C'])['graph'];self.assertFalse(g['assertion_paths'])
 def test_multi_support_is_not_probability(self):
  e=run(['CLAIM CAUSE A -> B','CLAIM CAUSE A -> B'])['graph']['edges'][0];self.assertEqual(e['evidence']['support_count'],2);self.assertTrue(e['evidence']['balance_not_probability'])
 def test_line_provenance(self):
  e=run(['CLAIM CAUSE A -> B','HYPOTHESIS CAUSE A -> B','DENY CAUSE A -> B'])['graph']['edges'][0];self.assertEqual(e['evidence']['uncertain_lines'],[2]);self.assertEqual(e['evidence']['counter_lines'],[3])
 def test_many_nodes_guard(self):
  from causal_graph_r04 import build_graph
  with self.assertRaises(ValueError):build_graph({'relationships':[{'source':'A','target':'B','evidence':[]}]},max_nodes=1)
if __name__=='__main__':unittest.main()
