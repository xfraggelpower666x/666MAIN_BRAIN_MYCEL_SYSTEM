import unittest
from engine.mandala import arrange
from engine.context_preset import evaluate
class MandalaTests(unittest.TestCase):
    def report(self, pos, neg=(), candidate=True):
        return dict(system_id='666TDI-001',mandala_candidate=candidate,signal_evidence={k:['x'] for k in pos},negated_signals={k:['x'] for k in neg})
    def test_rings(self):
        r=arrange(self.report(['MANTRA','SPACE','MOTION','DYNAMICS']))
        self.assertEqual(r['rings'][0]['functions'],['MANTRA']); self.assertEqual(r['rings'][3]['functions'],['SPACE']); self.assertTrue(r['low_stable']); self.assertFalse(r['automatic_promotion'])
    def test_negative(self): self.assertIsNone(arrange(self.report(['MANTRA','SPACE'],['MANTRA'])))
    def test_no_candidate(self): self.assertIsNone(arrange(self.report(['MANTRA','SPACE'],candidate=False)))
    def test_foreign(self):
        with self.assertRaises(ValueError): arrange({'system_id':'other'})
    def test_native_consumer(self):
        r=evaluate({'lyrics':'mantra, orbit, drop'})
        self.assertEqual(r['mandala_arrangement']['status'],'REVIEW_ONLY')
        self.assertFalse(r['preset_auto_save'])
