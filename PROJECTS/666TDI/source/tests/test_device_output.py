"""R1.3 device routes stay output-only; R1.0 music analysis stays identical."""
import unittest
from engine import device_output, daemon_cli


class DeviceOutputR13Tests(unittest.TestCase):
 def intent(self):
  return {
   "title":"Signal Return","genre":"Dark Psytrance","story":"Return from silence",
   "motor":"relentless forward motion","mid":"dense acid layers",
   "voice":"clear vocal","structure":"deep break and dynamic contrast",
   "lyrics":"A spoken word\nNow a return","avoid":"no static loop",
   "ending":"clear ending","bpm":148
  }

 def test_reject_missing_device(self):
  with self.assertRaisesRegex(ValueError,"DEVICE_PREFLIGHT_REQUIRED"):
   device_output.translate(self.intent(),None)

 def test_default_iphone_route_is_no_main(self):
  x=device_output.translate(self.intent(),"IPHONE_SUNO_APP")
  self.assertEqual(x["route"],"IPHONE_CUSTOM_NO_MAIN")
  self.assertIsNone(x["main_input"])
  self.assertEqual(x["pc_duration_control"]["visibility"],"NOT_CONFIRMED")

 def test_iphone_main_opt_in_preserves_empty(self):
  x=device_output.translate(self.intent(),"IPHONE_SUNO_APP",{"iphone_main_input":True,"main_input_text":""})
  self.assertEqual(x["route"],"IPHONE_CUSTOM_WITH_MAIN")
  self.assertEqual(x["main_input"]["text"],"")
  self.assertEqual(x["main_input"]["status"],"CREATOR_EXPLICIT_EMPTY_PRESERVED")

 def test_iphone_main_only_creator_text(self):
  x=device_output.translate(self.intent(),"IPHONE_SUNO_APP",{"iphone_main_input":True,"main_input_text":"My original event storyboard"})
  self.assertEqual(x["main_input"]["text"],"My original event storyboard")

 def test_no_main_does_not_smuggle_storyboard(self):
  with self.assertRaisesRegex(ValueError,"MAIN_INPUT_NOT_ENABLED"):
   device_output.translate(self.intent(),"IPHONE_SUNO_APP",{"iphone_main_input":False,"main_input_text":"unexpected"})

 def test_pc_main_is_forbidden(self):
  with self.assertRaisesRegex(ValueError,"MAIN_INPUT_NOT_AVAILABLE"):
   device_output.translate(self.intent(),"PC_SUNO_BROWSER",{"iphone_main_input":True})

 def test_pc_slider_unknown_not_available_for_duration(self):
  with self.assertRaisesRegex(ValueError,"PC_DURATION_NOT_CONFIRMED_VISIBLE"):
   device_output.translate(self.intent(),"PC_SUNO_BROWSER",{"pc_selected_duration":"5:40"})

 def test_pc_duration_when_visible(self):
  x=device_output.translate(self.intent(),"PC_SUNO_BROWSER",{"pc_duration_slider_visible":True,"pc_selected_duration":"5:40"})
  self.assertEqual(x["pc_duration_control"]["selected_duration"],"5:40")
  self.assertEqual(x["route"],"PC_BROWSER")

 def test_no_iphone_slider_assumption(self):
  with self.assertRaisesRegex(ValueError,"PC_DURATION_CONTROL_NOT_ALLOWED_ON_IPHONE"):
   device_output.translate(self.intent(),"IPHONE_SUNO_APP",{"pc_duration_slider_visible":True})

 def test_exact_utf16_including_emoji_newline(self):
  self.assertEqual(device_output.utf16_length("🌀\n"),3)
  x=device_output.translate({**self.intent(),"lyrics":"🌀\nA"},"IPHONE_SUNO_APP")
  self.assertEqual(x["fields"]["lyrics"]["utf16_units"],4)
  self.assertEqual(x["fields"]["lyrics"]["text"],"🌀\nA")

 def test_four_fields_exact_source_and_avoid_in_extended(self):
  x=device_output.translate(self.intent(),"PC_SUNO_BROWSER")
  self.assertEqual(x["field_order"],["title","extended","style","lyrics"])
  self.assertEqual(x["fields"]["lyrics"]["text"],self.intent()["lyrics"])
  self.assertIn("Avoid: no static loop",x["fields"]["extended"]["text"])
  self.assertNotIn("Avoid:",x["fields"]["style"]["text"])

 def test_over_budget_is_flagged_never_truncated(self):
  t={**self.intent(),"title":"A"*81}
  x=device_output.translate(t,"PC_SUNO_BROWSER")
  self.assertEqual(x["fields"]["title"]["text"],"A"*81)
  self.assertFalse(x["fields"]["title"]["copy_ready"])
  self.assertEqual(x["fields"]["title"]["status"],"OVER_REFERENCE_BUDGET_CREATOR_REVIEW")

 def test_no_mutation_to_intent(self):
  t=self.intent();before=dict(t)
  device_output.translate(t,"IPHONE_SUNO_APP")
  self.assertEqual(t,before)

 def test_daemon_same_music_analysis_both_devices(self):
  t=self.intent()
  a=daemon_cli.preanalysis({"device":"IPHONE_SUNO_APP","intent":t})
  b=daemon_cli.preanalysis({"device":"PC_SUNO_BROWSER","intent":t})
  self.assertEqual(a["semantic"],b["semantic"])
  self.assertEqual(a["causal"],b["causal"])
  self.assertEqual(a["preanalysis"],b["preanalysis"])
  self.assertNotEqual(a["device_output"]["route"],b["device_output"]["route"])

 def test_daemon_ui_has_device_output_and_copy_fields(self):
  html=daemon_cli.STATIC.read_text(encoding="utf-8")
  for marker in ['id="iphone-main-choice"','id="pc-slider-choice"','id="device-output-fields"','function renderDeviceOutput(data)','route_context:readRoute()']:
   self.assertIn(marker,html)

if __name__=="__main__":
 unittest.main()
