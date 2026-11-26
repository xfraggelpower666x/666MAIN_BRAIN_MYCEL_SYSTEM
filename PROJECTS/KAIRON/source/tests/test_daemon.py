"""Focused local tests for the R1.1 daemon and existing R1.0 engine."""
import json
import unittest
from pathlib import Path
from engine import daemon_cli


class DaemonTests(unittest.TestCase):
 def example(self):
  return {"device":"IPHONE_SUNO_APP","intent":{
   "title":"Creative Causal Journey","genre":"Dark Psytrance","bpm":148,
   "motor":"stable sub, relentless forward motion","mid":"dense acid layers",
   "voice":"clear vocal","structure":"deep break and dynamic contrast"}}

 def test_device_selection_required(self):
  p=self.example();p.pop("device")
  with self.assertRaisesRegex(ValueError,"DEVICE_PREFLIGHT_REQUIRED"):
   daemon_cli.preanalysis(p)

 def test_unknown_device_rejected(self):
  p=self.example();p["device"]="UNVERIFIED_AUTOMATIC_MODE"
  with self.assertRaisesRegex(ValueError,"DEVICE_PREFLIGHT_REQUIRED"):
   daemon_cli.preanalysis(p)

 def test_iphone_selection_preserved(self):
  x=daemon_cli.preanalysis(self.example())
  self.assertEqual(x["device"],"IPHONE_SUNO_APP")
  self.assertEqual(x["stage"],"CREATOR_DECISION_REVIEW")
  self.assertFalse(x["renderer_executed"])

 def test_pc_device_has_same_music_reasoning(self):
  p=self.example()
  a=daemon_cli.preanalysis(p)
  p["device"]="PC_SUNO_BROWSER"
  b=daemon_cli.preanalysis(p)
  self.assertEqual(a["causal"],b["causal"])
  self.assertEqual(a["semantic"],b["semantic"])

 def test_causal_is_real_r10_result(self):
  x=daemon_cli.preanalysis(self.example())
  self.assertEqual(x["causal"]["system_id"],"666TDI-001")
  self.assertTrue(x["causal"]["emergences"])
  self.assertTrue(x["causal"]["read_only"])

 def test_potential_collision_not_an_audio_defect(self):
  x=daemon_cli.preanalysis(self.example())
  self.assertTrue(any(set(c["functions"])=={"VOICE_CLARITY","DENSE_LAYERS"} for c in x["causal"]["collisions"]))
  self.assertTrue(all(c["automatic_error"] is False for c in x["causal"]["collisions"]))

 def test_empty_musical_intent_rejected(self):
  with self.assertRaisesRegex(ValueError,"MUSICAL_INTENT_REQUIRED"):
   daemon_cli.preanalysis({"device":"PC_SUNO_BROWSER","intent":{"title":"Only Title"}})

 def test_bad_bpm_rejected(self):
  p=self.example();p["intent"]["bpm"]=400
  with self.assertRaisesRegex(ValueError,"INVALID_BPM"):
   daemon_cli.preanalysis(p)

 def test_creator_input_unchanged(self):
  p=self.example();before=json.dumps(p,sort_keys=True)
  daemon_cli.preanalysis(p)
  self.assertEqual(json.dumps(p,sort_keys=True),before)

 def test_no_cross_system_learning(self):
  x=daemon_cli.preanalysis(self.example())
  self.assertTrue(x["read_only"])
  self.assertTrue(x["no_global_learning"])
  self.assertFalse(x["suno_generation"])

 def test_static_ui_exists_and_contains_required_controls(self):
  html=daemon_cli.STATIC.read_text(encoding="utf-8")
  self.assertIn('data-device="IPHONE_SUNO_APP"',html)
  self.assertIn('data-device="PC_SUNO_BROWSER"',html)
  self.assertIn('id="analyze-button" disabled',html)
  self.assertIn('id="decision-list"',html)
  self.assertIn('id="relation-list"',html)
  self.assertIn('id="download-button"',html)


if __name__ == "__main__":
 unittest.main()
