"""R1.2 track preanalysis: explicit timing, provenance and non-destructive relation projections."""
import unittest
from engine import track_preanalysis, semantic_intelligence, creative_causal, daemon_cli


def evaluation(intent, bars=None):
 sem=semantic_intelligence.assess(intent)
 causal=creative_causal.assess(intent)
 return track_preanalysis.assess(intent,sem,causal,total_bars=bars)


class TrackPreanalysisR12Tests(unittest.TestCase):
 def example(self):
  return {
   "bpm":148,"motor":"relentless forward motion stable sub","mid":"dense acid layers",
   "voice":"clear vocal","structure":"deep break and dynamic contrast, evolving variation",
   "energy":"build tension","ending":"final release and clear ending"
  }

 def test_no_time_invention_without_explicit_bars(self):
  x=evaluation(self.example())
  self.assertIsNone(x["planned_duration_seconds"])
  self.assertTrue(all(c["bars"] is None for c in x["chapters"]))

 def test_exact_224_bars_no_loss(self):
  x=evaluation(self.example(),224)
  self.assertEqual(sum(c["bars"] for c in x["chapters"]),224)
  self.assertEqual(x["chapters"][0]["start_bar_zero_based"],0)
  self.assertEqual(x["chapters"][-1]["end_bar_exclusive"],224)

 def test_duration_is_theoretical_4_4(self):
  x=evaluation(self.example(),224)
  self.assertAlmostEqual(x["planned_duration_seconds"],224*4*60/148,places=2)
  self.assertEqual(x["duration_status"],"THEORETICAL_4_4_PLANNED_BARS_NOT_RENDER_DURATION")

 def test_not_audio_measured(self):
  x=evaluation(self.example(),224)
  self.assertFalse(x["audio_verified"])
  self.assertTrue(all(c["relative_energy_type"]=="ILLUSTRATIVE_DESIGN_HYPOTHESIS" for c in x["chapters"]))

 def test_layer_fields_and_evidence(self):
  x=evaluation(self.example())
  layers={item["layer"]:item for item in x["layers"]}
  self.assertTrue(layers["LOW"]["provided"])
  self.assertTrue(layers["MID"]["provided"])
  self.assertTrue(layers["VOICE"]["provided"])
  self.assertFalse(layers["HIGH"]["provided"])
  self.assertIn("LOW_ANCHOR",layers["LOW"]["supported_functions"])

 def test_emergent_alternatives_have_tradeoffs(self):
  x=evaluation(self.example())
  self.assertTrue(x["alternatives"])
  self.assertTrue(all(a["creator_selection_required"] and not a["automatic_choice"] for a in x["alternatives"]))
  self.assertTrue(all(a["option_b"]["tradeoff"] for a in x["alternatives"]))

 def test_empty_semantics_stays_optional(self):
  x=evaluation({"title":"Untitled","bpm":148})
  self.assertEqual(x["alternatives"],[])
  self.assertTrue(all(c["status"]=="OPTIONAL_CREATOR_REVIEW" for c in x["chapters"]))

 def test_invalid_bar_target(self):
  for x in (0,31,2049,True,3.14):
   with self.subTest(value=x),self.assertRaises(ValueError):
    evaluation(self.example(),x)

 def test_foreign_authority_rejected(self):
  with self.assertRaisesRegex(ValueError,"FOREIGN_ANALYSIS_NOT_ALLOWED"):
   track_preanalysis.assess(self.example(),{"system_id":"LYVRA"},{"system_id":"666TDI-001"})

 def test_no_mutation_and_no_story_invention(self):
  intent=self.example();before=dict(intent)
  x=evaluation(intent,224)
  self.assertEqual(before,intent)
  self.assertTrue(x["no_story_invention"])
  self.assertTrue(x["read_only"])

 def test_endpoint_device_gate_still_required(self):
  with self.assertRaisesRegex(ValueError,"DEVICE_PREFLIGHT_REQUIRED"):
   daemon_cli.preanalysis({"intent":self.example(),"total_bars":224})

 def test_endpoint_integrates_forecast(self):
  x=daemon_cli.preanalysis({"device":"IPHONE_SUNO_APP","intent":self.example(),"total_bars":"224"})
  self.assertEqual(x["preanalysis"]["bar_target"],224)
  self.assertEqual(x["preanalysis"]["system_id"],"666TDI-001")
  self.assertFalse(x["renderer_executed"])

 def test_device_switch_preserves_musical_forecast(self):
  a=daemon_cli.preanalysis({"device":"IPHONE_SUNO_APP","intent":self.example(),"total_bars":224})
  b=daemon_cli.preanalysis({"device":"PC_SUNO_BROWSER","intent":self.example(),"total_bars":224})
  self.assertEqual(a["preanalysis"],b["preanalysis"])

if __name__=="__main__":
 unittest.main()
