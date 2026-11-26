import tempfile,unittest,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import portable as p
from engine import evolution as e
class EvolutionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.orig=p.DATA;p.DATA=Path(self.temp.name)
  self.intent=json.loads((p.ROOT/'examples'/'intent.json').read_text(encoding='utf-8'))
 def tearDown(self):p.DATA=self.orig;self.temp.cleanup()
 def test_identity_masculine(self):
  self.assertEqual(e.identity()['character']['pronoun_de'],'er')
  self.assertEqual(e.character_readback()['state']['character_name'],'666TDI')
 def test_current_not_foreign(self):
  self.assertEqual(e.identity()['authority'],'LOCAL_666TDI_ONLY')
  self.assertFalse(e.comprehensive_status()['foreign_repo_write_allowed'])
 def test_base_is_untouched(self):self.assertEqual(p.start()['status'],'VERIFIZIERT_LOCAL')
 def test_additive_cannot_promote_old_history(self):
  q=e.add_proposal('controlled_aperture','lyvra-historical',{'x':1})
  self.assertFalse(q['is_current_authority']);self.assertEqual(q['status'],'CANDIDATE')
 def test_unknown_module_rejected(self):
  with self.assertRaises(e.EvidenceError):e.add_proposal('foreign-master','x',{})
 def test_tension_resolution(self):
  self.assertEqual(e.predictive_tension([{'type':'EXPECT','anchor':'a'},{'type':'RESOLVE','anchor':'a'}])['status'],'STRUCTURAL_MODEL_OK')
  self.assertEqual(e.predictive_tension([{'type':'EXPECT','anchor':'a'}])['status'],'PARTIAL')
 def test_pressure_contrast(self):
  self.assertEqual(e.pressure_arc()['status'],'STRUCTURAL_MODEL_OK')
  self.assertEqual(e.pressure_arc(['BODY_LOCK','LOAD','IMPACT_RETURN'])['status'],'PARTIAL')
 def test_sound_object_complete(self):
  s=e.sound_object('creator','ACID','metal','intro','orbit','distortion','rising','hardstop')
  self.assertFalse(s['audio_presence_verified'])
  with self.assertRaises(e.EvidenceError):e.sound_object('creator','ACID','metal','intro','','distortion','rising','hardstop')
 def test_mix_does_not_fake_audio(self):
  self.assertEqual(e.conflict_candidates('VOICE','ACID')['status'],'UNVERIFIED_WITHOUT_STEMS')
 def test_temporal_addition_not_erasure(self):
  t=p.create_track(self.intent)['track_id']
  x=e.temporal_feedback(t,'IMMEDIATE_RESONANCE','strong')
  y=e.temporal_feedback(t,'SETTLED_REFLECTION','too busy')
  ledger=p.load(p.DATA/'temporal_feedback.json')
  self.assertEqual(len(ledger['entries']),2)
  self.assertIsNone(y['supersedes'])
  with self.assertRaises(e.EvidenceError):e.temporal_feedback(t,'SYNTHESIS','erase previous',supersedes=x['id'])
  z=e.temporal_feedback(t,'SYNTHESIS','explicit correction',context={'explicit_creator_retraction':True},supersedes=x['id'])
  self.assertEqual(z['supersedes'],x['id'])
 def test_character_proposal_not_auto_apply(self):
  q=e.character_proposal('humor','dry','creator response','source-1')
  self.assertEqual(q['status'],'CANDIDATE')
  self.assertEqual(e.character_readback()['state']['traits'],{})
 def test_aperture_no_audio_claim(self):
  q=e.aperture_geometry('high','narrow','center','hard','closing')
  self.assertFalse(q['not_audio_verified'] is False)
if __name__=='__main__':unittest.main()
