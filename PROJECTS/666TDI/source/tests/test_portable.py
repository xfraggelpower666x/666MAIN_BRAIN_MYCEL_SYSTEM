import json,sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import portable as p

class PortableTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.original=p.DATA;p.DATA=Path(self.tmp.name)
  self.intent=json.loads((p.ROOT/'examples'/'intent.json').read_text())
 def tearDown(self):p.DATA=self.original;self.tmp.cleanup()
 def test_local_start(self):self.assertEqual(p.start()['status'],'VERIFIZIERT_LOCAL')
 def test_no_foreign_write(self):self.assertFalse(p.start()['state']['foreign_repo_write_allowed'])
 def test_isolation(self):
  a=p.create_track(self.intent);b=p.create_track({**self.intent,'title':'another','lyrics':'different'})
  self.assertNotEqual(a['track_id'],b['track_id']);self.assertNotIn('different',a['lyrics'])
 def test_analysis_pure_source(self):
  a=p.create_track(self.intent);b=p.analyze(a);self.assertEqual(b['lyrics'],self.intent['lyrics'])
 def test_cards_are_candidates(self):
  b=p.analyze(p.create_track(self.intent));self.assertTrue(b['analysis']['active_cards']);self.assertTrue(all(c['status']=='CANDIDATE_CONTEXT_REVIEW' for c in b['analysis']['active_cards']))
 def test_compiler_underrun_warns(self):
  b=p.analyze(p.create_track(self.intent));r=p.compiler(b,'lyria2_asg');self.assertIn('DURATION_EXCEEDS_HISTORICAL_RENDERER_LIMIT',r['warnings'])
 def test_ledger_no_auto_promotion(self):
  a=p.create_track(self.intent);o=p.record_feedback(a['track_id'],'ace_step_asg','bass too bouncy');self.assertFalse(o['global_rule']);self.assertEqual(p.promotion_gate([o['id']])['status'],'BLOCKIERT')
 def test_rehydrate_integrity(self):
  a=p.create_track(self.intent);s=p.rehydrate();self.assertEqual(s['status'],'VERIFIZIERT_LOCAL')
  data=p.load(p.DATA/'livecircle.json');data['events'][0]['kind']='COMPILED';p.atomic(p.DATA/'livecircle.json',data)
  self.assertEqual(p.rehydrate()['status'],'PARTIAL')
 def test_handoff(self):
  p.start();p.handoff();self.assertTrue((p.DATA/'handoff.json').exists())
 def test_no_auto_previous_hook(self):
  first=p.create_track({**self.intent,'lyrics':'A unique hook X'});second=p.create_track({**self.intent,'title':'Next','lyrics':'A new hook Y'})
  self.assertNotIn('unique hook X',json.dumps(second))
 def test_no_unknown_event(self):
  with self.assertRaises(ValueError):p.event('FOREIGN_REPO_WRITE',{})
 def test_intent_unchanged(self):
  a=p.create_track(self.intent);orig=json.loads(json.dumps(a));p.analyze(a);self.assertEqual(a,orig)

if __name__=='__main__': unittest.main()
