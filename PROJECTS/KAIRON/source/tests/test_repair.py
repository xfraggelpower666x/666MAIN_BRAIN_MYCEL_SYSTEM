import unittest
from engine.context_preset import evaluate
class Repair(unittest.TestCase):
    def test_field_scope(self):
        r=evaluate({'motor':'no rolling bass','high':'stereo orbit','lyrics':'mantra'})
        self.assertIn('orbit',r['signal_evidence']['SPACE'])
        self.assertTrue(r['mandala_candidate'])
    def test_conflict(self):
        r=evaluate({'lyrics':'mantra, orbit','voice':'no mantra'})
        self.assertFalse(r['mandala_candidate'])
        self.assertIsNone(r['mandala_arrangement'])
    def test_positive(self):
        r=evaluate({'lyrics':'mantra, orbit, drop'})
        self.assertTrue(r['mandala_candidate'])
        self.assertEqual(r['mandala_arrangement']['status'],'REVIEW_ONLY')
        self.assertFalse(r['preset_auto_save'])
    def test_foreign(self):
        with self.assertRaises(ValueError): evaluate({'system_id':'LYVRA'})
