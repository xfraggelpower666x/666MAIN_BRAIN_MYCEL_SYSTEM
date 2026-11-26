import unittest
from engine import creative_causal as c

class CreativeCausalR10Tests(unittest.TestCase):
 def test_motor_and_contrast_emerge(self):
  x=c.assess({"motor":"relentless forward motion","structure":"deep break and dynamic contrast"})
  self.assertIn("PRESSURE_RELEASE_WITH_MOTOR_ANCHOR",{v["id"] for v in x["emergences"]})
 def test_low_anchor_and_spatial_motion_complement(self):
  x=c.assess({"motor":"stable sub and dry kick","high":"wide stereo orbit spatial motion"})
  v=next(v for v in x["relations"] if set(v["functions"])=={"LOW_ANCHOR","SPATIAL_MOTION"})
  self.assertEqual(v["relation"],"COMPLEMENTARY")
 def test_voice_layer_tension_not_error(self):
  x=c.assess({"voice":"clear vocal","mid":"dense acid layers"})
  v=next(v for v in x["emergences"] if v["id"]=="VOICE_LAYER_NEGOTIATION")
  self.assertEqual(v["status"],"CREATIVE_EMERGENCE_CANDIDATE")
  self.assertTrue(all(not z["automatic_error"] for z in x["collisions"]))
 def test_arrangement_does_not_claim_audio_resolution(self):
  x=c.assess({"voice":"clear vocal","mid":"dense acid layers","structure":"sparse verse then return; separate sections"})
  v=next(v for v in x["collisions"] if set(v["functions"])=={"VOICE_CLARITY","DENSE_LAYERS"})
  self.assertEqual(v["status"],"SEQUENCING_OR_ARRANGEMENT_MAY_RESOLVE")
  self.assertTrue(v["not_a_proven_audio_defect"])
 def test_transforming_recurrence(self):
  x=c.assess({"lyrics":"recurring mantra","structure":"evolving transformation"})
  self.assertIn("TRANSFORMING_RECURRENCE",{v["id"] for v in x["emergences"]})
 def test_expectation_payoff(self):
  x=c.assess({"energy":"build tension","ending":"final release"})
  self.assertTrue(any(v["id"]=="EXPECTATION_PAYOFF" for v in x["emergences"]))
 def test_empty_input_does_not_invent(self):
  x=c.assess({"title":"Untitled"})
  self.assertEqual(x["status"],"INSUFFICIENT_SEMANTIC_EVIDENCE")
  self.assertEqual(x["emergences"],[])
 def test_read_only_track_local(self):
  t={"track_id":"r10-test","motor":"forward motion","structure":"dynamic contrast"}; before=dict(t)
  x=c.assess(t)
  self.assertEqual(t,before); self.assertEqual(x["system_id"],"666TDI-001")
  self.assertTrue(x["read_only"]); self.assertFalse(x["global_promotion"]); self.assertFalse(x["renderer_override"])
 def test_reuses_native_semantic_report(self):
  from unittest.mock import patch
  t={'track_id':'reuse','lyrics':'mantra','structure':'evolving transformation'}
  sem=c.semantic.assess(t); expected=c.assess(t)
  with patch.object(c.semantic,'assess',side_effect=AssertionError('duplicate semantic analysis')):
   self.assertEqual(c.assess(t,semantic_report=sem),expected)
 def test_rejects_foreign_semantic_scope(self):
  t={'track_id':'a'}; sem=c.semantic.assess(t)
  for key,value in [('track_id','b'),('system_id','foreign'),('schema','foreign')]:
   with self.assertRaisesRegex(ValueError,'SEMANTIC_SCOPE_MISMATCH'):
    c.assess(t,semantic_report={**sem,key:value})
 def test_invalid_input(self):
  with self.assertRaises(ValueError): c.assess("not an object")

if __name__=="__main__": unittest.main()
