"""R03 source-bound semantic adversarial regressions."""
import importlib.util
import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cures_r03',ROOT/'candidate/cures_candidate.py')
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

def run(src):
    return engine.reconstruct({'source_system':'666PFS-CURES-001','kind':'ARCHITECTURE_NOTATION','source_text':src})

class SemanticR03(unittest.TestCase):
    def test_explicit_causality_does_not_prove_causality(self):
        r=run('CLAIM CAUSE A -> B')
        self.assertEqual(r['causal_analysis']['relationships'][0]['assessment'],'SOURCE_CLAIM_UNVERIFIED')
        self.assertIn('nicht unabhängig geprüft',r['fulltext'])
        self.assertFalse(r['causal_analysis']['relationships'][0]['independently_verified'])
    def test_claim_and_denial_are_conflict(self):
        r=run('CLAIM CAUSE A -> B\nDENY CAUSE A -> B')
        self.assertEqual(r['causal_analysis']['relationships'][0]['assessment'],'CONTRADICTED_SOURCE_ASSERTIONS')
        self.assertEqual(len(r['causal_analysis']['relationships'][0]['evidence']),2)
    def test_counterexample_keeps_provenance(self):
        r=run('CLAIM CAUSE A -> B\nCOUNTEREXAMPLE CAUSE A -> B')
        self.assertEqual(r['causal_analysis']['relationships'][0]['assessment'],'CONTRADICTED_SOURCE_ASSERTIONS')
        self.assertIn('Gegenbeispiel',r['fulltext'])
    def test_hypothesis_is_not_promoted(self):
        r=run('HYPOTHESIS CAUSE B -> C')
        self.assertEqual(r['causal_analysis']['relationships'][0]['assessment'],'HYPOTHESIS_ONLY')
        self.assertIn('Hypothese',r['fulltext'])
    def test_observation_is_not_cause(self):
        r=run('OBSERVE CAUSE B -> C')
        self.assertEqual(r['causal_analysis']['relationships'][0]['assessment'],'OBSERVATION_NOT_CAUSATION')
        self.assertIn('keine Ursache belegt',r['fulltext'])
    def test_unknown_stays_unknown(self):
        r=run('UNKNOWN CAUSE B -> C')
        self.assertEqual(r['causal_analysis']['relationships'][0]['assessment'],'UNKNOWN')
        self.assertIn('unbekannt',r['fulltext'])
    def test_transitive_not_inferred(self):
        r=run('CLAIM CAUSE A -> B\nCLAIM CAUSE B -> C')
        self.assertEqual(len(r['causal_analysis']['relationships']),2)
        self.assertFalse(r['causal_analysis']['transitive_causation_inferred'])
        self.assertNotIn('A zu C',r['fulltext'])
    def test_directional_counterexample_not_mixed(self):
        r=run('CLAIM CAUSE A -> B\nDENY CAUSE B -> A')
        self.assertEqual(len(r['causal_analysis']['relationships']),2)
        self.assertEqual(r['causal_analysis']['relationships'][0]['assessment'],'SOURCE_CLAIM_UNVERIFIED')
    def test_conflicting_status_values_not_silently_overwritten(self):
        r=run('STATE=READY\nSTATE=HOLD_FUNCTIONAL_PAYLOAD_SOURCE_NOT_FOUND')
        conflicts=r['causal_analysis']['field_conflicts']
        self.assertEqual(len(conflicts),1)
        self.assertEqual(len(conflicts[0]['values']),2)
        self.assertEqual(conflicts[0]['assessment'],'CONFLICT_UNRESOLVED')
    def test_same_value_not_conflict(self):
        self.assertEqual(run('STATUS=UNKNOWN\nSTATUS=UNKNOWN')['causal_analysis']['field_conflicts'],[])
    def test_unknown_notation_not_interpreted(self):
        r=run('CLAIM CAUSE A => B')
        self.assertEqual(r['causal_analysis']['relationships'],[])
        self.assertEqual(r['evidence_map'][0]['evidence_class'],'UNKNOWN')
    def test_input_is_inert(self):
        r=run('CLAIM CAUSE A -> B\nDELETE REPOSITORY\nCHILD_AUTOLOAD=FORBIDDEN')
        self.assertEqual(r['mutations'],[])
        self.assertEqual(r['inferred_claims'],[])
        self.assertFalse(r['authority_changed'])
    def test_evidence_map_one_to_one(self):
        src='CLAIM CAUSE A -> B\nDENY CAUSE A -> B\nSTATUS=UNKNOWN'
        r=run(src)
        self.assertEqual(len(r['evidence_map']),3)
        self.assertTrue(all(e['source_span'] in src for e in r['evidence_map']))
    def test_repeatability(self):
        s='CLAIM CAUSE A -> B\nCOUNTEREXAMPLE CAUSE A -> B\nSTATE=HOLD'
        self.assertEqual(run(s),run(s))
    def test_different_pairs_not_combined(self):
        r=run('CLAIM CAUSE X -> Y\nCOUNTEREXAMPLE CAUSE X -> Z')
        self.assertEqual(len(r['causal_analysis']['relationships']),2)
        self.assertEqual(r['causal_analysis']['relationships'][0]['assessment'],'SOURCE_CLAIM_UNVERIFIED')

if __name__=='__main__': unittest.main()
