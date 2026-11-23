"""R1.4 — real local creator evidence tests; no Suno or audio simulation."""
import tempfile
import unittest
from pathlib import Path
from engine import creator_learning as l

class CreatorLearningTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)
  self.payload={"track_id":"track-01","decision_id":"VOICE_LAYER_NEGOTIATION",
   "category":"VOICE","rating":"SUCCESS","intent_summary":"clear voice against acid",
   "observed_outcome":"words understandable in recorded result",
   "creator_note":"I listened","device_route":"IPHONE_CUSTOM_NO_MAIN","creator_confirmed":True}

 def test_explicit_confirmation_required(self):
  with self.assertRaisesRegex(ValueError,"CREATOR_CONFIRMATION_REQUIRED"):
   l.prepare({**self.payload,"creator_confirmed":False})

 def test_creator_feedback_is_not_audio_proof(self):
  x=l.prepare(self.payload,now="2026-11-23T12:00:00+00:00")
  self.assertFalse(x["audio_measured_by_tdi"]);self.assertFalse(x["causal_proof"]);self.assertFalse(x["global_rule"])

 def test_local_persistence_and_readback(self):
  x=l.record(self.root,self.payload)
  self.assertEqual(x["status"],"TRACK_LOCAL_CREATOR_EVIDENCE_RECORDED")
  r=l.assess(self.root,"track-01")
  self.assertEqual(r["observations"],1);self.assertEqual(r["relations"][0]["status"],"SINGLE_OUTCOME_CANDIDATE")

 def test_path_traversal_rejected(self):
  for value in ("../x","a/b","\\tmp",".secret"):
   with self.subTest(value=value),self.assertRaises(ValueError):
    l.record(self.root,{**self.payload,"track_id":value})

 def test_contradictions_remain_visible(self):
  l.record(self.root,self.payload)
  l.record(self.root,{**self.payload,"rating":"UNSUCCESSFUL","observed_outcome":"vocal masked in second render"})
  r=l.assess(self.root,"track-01")
  self.assertTrue(r["has_contradictions"])
  self.assertEqual(r["relations"][0]["status"],"CONTRADICTORY_OUTCOMES_REVIEW_REQUIRED")
  self.assertEqual(len(r["relations"][0]["evidence_ids"]),2)

 def test_tamper_detected_on_readback(self):
  l.record(self.root,self.payload)
  path=self.root/"creator_evidence"/"track-01.jsonl"
  path.write_text(path.read_text().replace("SUCCESS","UNSUCCESSFUL"))
  with self.assertRaisesRegex(ValueError,"EVIDENCE_HASH_MISMATCH"):l.assess(self.root,"track-01")

 def test_isolated_tracks(self):
  l.record(self.root,self.payload)
  self.assertEqual(l.assess(self.root,"track-02")["observations"],0)

 def test_artifact_hash_does_not_fabricate_file(self):
  with self.assertRaisesRegex(ValueError,"INVALID_ARTIFACT_SHA256"):
   l.prepare({**self.payload,"artifact_sha256":"fake.mp3"})

 def test_repeated_outcomes_are_not_global_learning(self):
  l.record(self.root,self.payload)
  l.record(self.root,{**self.payload,"creator_note":"Another take","observed_outcome":"still fine"})
  report=l.assess(self.root,"track-01")
  self.assertEqual(report["relations"][0]["status"],"REPEATED_TRACK_LOCAL_OBSERVATION_NOT_GENERALIZED")
  self.assertFalse(report["global_promotion"])

 def test_assess_does_not_write(self):
  l.record(self.root,self.payload)
  path=self.root/"creator_evidence"/"track-01.jsonl"
  before=path.read_bytes()
  l.assess(self.root,"track-01")
  self.assertEqual(before,path.read_bytes())

 def test_empty_review_before_any_feedback(self):
  self.assertEqual(l.assess(self.root,"track-01")["status"],"NO_CREATOR_EVIDENCE")

 def test_invalid_creator_fields(self):
  for updates in ({"category":"MADE_UP"},{"rating":"GOLD"},{"observed_outcome":""},
                  {"decision_id":""},{"device_route":"FORGED"},{"creator_confirmed":"true"}):
   with self.subTest(updates=updates),self.assertRaises(ValueError):
    l.prepare({**self.payload,**updates})

if __name__=="__main__":unittest.main()
