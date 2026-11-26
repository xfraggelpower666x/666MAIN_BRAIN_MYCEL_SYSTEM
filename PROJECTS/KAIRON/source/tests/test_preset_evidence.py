import unittest
from engine.context_preset import evaluate

class CausalProjectionTests(unittest.TestCase):
    def report(self, **changes):
        item = dict(id='TRANSFORMING_RECURRENCE', functions=['REPETITION','VARIATION'], evidence={'REPETITION':[{'field':'lyrics'}],'VARIATION':[{'field':'structure'}]}, constraints=[], status='CREATIVE_EMERGENCE_CANDIDATE')
        item.update(changes)
        return dict(system_id='666TDI-001', schema='666TDI_CREATIVE_CAUSAL_R10_V1', track_id='a', emergences=[item], collisions=[])
    def track(self):
        return dict(track_id='a',lyrics='mantra, orbit',motor='rolling bass',mid='acid',structure='build, drop')
    def test_both_consumers(self):
        r=evaluate(self.track(),causal_report=self.report())
        for x in (r['preset_candidate'],r['mandala_arrangement']):
            self.assertEqual(x['causal_evidence']['candidates'][0]['id'],'TRANSFORMING_RECURRENCE')
            self.assertFalse(x['causal_evidence']['automatic_promotion'])
    def test_constraint(self):
        r=evaluate(self.track(),causal_report=self.report(constraints=['VARIATION']))
        self.assertFalse(r['causal_evidence']['candidates'])
        self.assertEqual(len(r['causal_evidence']['counterevidence']),1)
    def test_scope(self):
        report=self.report(); report['track_id']='b'
        with self.assertRaisesRegex(ValueError,'CAUSAL_SCOPE_MISMATCH'): evaluate(self.track(),causal_report=report)
    def test_missing_evidence(self):
        r=evaluate(self.track(),causal_report=self.report(evidence={'REPETITION':[]}))
        self.assertFalse(r['causal_evidence']['candidates'])
