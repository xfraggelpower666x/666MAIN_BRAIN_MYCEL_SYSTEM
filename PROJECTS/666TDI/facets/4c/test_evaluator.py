import importlib.util
import sys
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location("tdi4c",Path(__file__).with_name("evaluator.py"))
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)

class FourCTests(unittest.TestCase):
    def test_identity(self): self.assertEqual(module.analyze({})["system_id"],"666TDI-001")
    def test_no_audio_gate(self): self.assertFalse(module.analyze({})["audio_analysis_required"])
    def test_missing(self): self.assertEqual(sum(x["result"]=="unverified" for x in module.analyze({})["findings"]),5)
    def test_bpm_is_profile(self): self.assertTrue(any(x["rule"]=="BPM_PROFILE" for x in module.analyze({"bpm":150})["findings"]))
    def test_break_not_rejected(self): self.assertTrue(any(x["rule"]=="KICK_BREAK" for x in module.analyze({"sections":[{"name":"break","bars":16,"kick_removed":True} ]})["findings"]))
    def test_clone_is_candidate(self):
        dna={"hook_type":"a","rhythm_type":"b","voice_mode":"c"}
        self.assertTrue(any(x["result"]=="candidate_similarity" for x in module.analyze({"dna":dna},{"dna":dna})["findings"]))
    def test_no_mutation(self):
        a={"layers":{"core":True}}; prior=repr(a);module.analyze(a);self.assertEqual(repr(a),prior)
    def test_chaos_flag(self): self.assertTrue(any(x["rule"]=="CHAOS_CONTEXT" for x in module.analyze({"sections":[{"name":"verse","bars":32,"chaos":True}]})["findings"]))
if __name__=="__main__": unittest.main()
