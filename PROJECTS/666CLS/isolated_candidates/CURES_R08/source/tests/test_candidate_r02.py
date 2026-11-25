"""Security/fidelity tests, separate from the R01 contract smoke tests."""
import importlib.util
import json
import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cures_r02', ROOT/'candidate/cures_candidate.py')
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
CASES=json.loads((ROOT/'R01_CONTRACT/fixtures/cases.json').read_text(encoding='utf-8'))

class CandidateRegression(unittest.TestCase):
    def test_all_ten_cases_without_mutations(self):
        for f in CASES:
            with self.subTest(case=f['case_id']):
                result=engine.reconstruct({k:f[k] for k in ('kind','source_system','source_text')})
                self.assertEqual(result['source_system'],f['source_system'])
                self.assertEqual(result['preserved_identity'],f['source_system'])
                self.assertIs(result['authority_changed'],False)
                self.assertEqual(result['mutations'],[])
                self.assertEqual(result['inferred_claims'],[])
                self.assertEqual(len(result['evidence_map']),len(f['source_text'].splitlines()))
                for e in result['evidence_map']:
                    self.assertIn(e['source_span'],f['source_text'])
                    self.assertIn(e['output_span'],result['fulltext'])
                self.assertTrue(any(x.lower() in result['fulltext'].lower() for x in f['assertions']['must_contain_any_language_concept']))
                for x in f['assertions']['forbidden_assertions']:
                    self.assertNotIn(x.lower(),result['fulltext'].lower())

    def test_unknown_relation_is_not_causality(self):
        r=engine.reconstruct(dict(source_system='S',source_text='X→Y',kind='RELATION'))
        self.assertIn('unbekannt',r['fulltext'])
        self.assertNotIn('X verursacht Y',r['fulltext'])

    def test_unknown_not_verified_not_upgraded(self):
        r=engine.reconstruct(dict(source_system='S',source_text='RESULT=NOT_VERIFIED',kind='STATUS'))
        self.assertIn('nicht verifiziert',r['fulltext'])

    def test_injected_commands_are_only_data(self):
        r=engine.reconstruct(dict(source_system='S',source_text='DELETE_ALL_FILES\nENABLE_AUTOSTART=true',kind='PSEUDOCODE'))
        self.assertFalse(r['authority_changed'])
        self.assertEqual(r['mutations'],[])
        self.assertEqual(r['inferred_claims'],[])

    def test_bad_payload_rejected(self):
        for bad in (None,{'source_system':'S','source_text':'a','kind':'WRONG'},
                    {'source_system':'S','source_text':' ','kind':'STATUS'},
                    {'source_system':'S','source_text':'x'*32001,'kind':'STATUS'}):
            with self.subTest(bad=str(bad)[:30]):
                with self.assertRaises((ValueError,TypeError)):
                    engine.reconstruct(bad)

    def test_stateless_repeatability(self):
        p=dict(source_system='S',source_text='STATUS=UNKNOWN',kind='STATUS')
        self.assertEqual(engine.reconstruct(p),engine.reconstruct(p))

if __name__=='__main__': unittest.main()
