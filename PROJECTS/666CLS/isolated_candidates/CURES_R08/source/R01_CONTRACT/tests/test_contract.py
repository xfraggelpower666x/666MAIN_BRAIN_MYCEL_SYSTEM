import json, pathlib, unittest, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
class ContractSelfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=load('contracts/CURES_CONTRACT_R01.json')
        cls.cases=load('fixtures/cases.json')
        cls.s=load('evidence/SOURCE_BINDINGS.json')
    def test_identity(self):
        self.assertEqual(self.c['system_identity'],'666PFS-CURES-001')
        self.assertEqual(self.c['entry_id'],'CURES-16001')
        self.assertEqual(self.c['status'],'PROPOSED_ISOLATED_NONEXECUTABLE')
    def test_no_authority_change(self):
        for k in ('original_authority_preserved','cross_system_merge_forbidden','child_autoload_forbidden','global_controller_forbidden','foreign_mutations_forbidden'):
            self.assertTrue(self.c['invariants'][k])
    def test_no_unverified_promotion(self):
        self.assertEqual(self.c['gates']['PFS_CURRENT'],'HOLD_FUNCTIONAL_PAYLOAD_SOURCE_NOT_FOUND')
        self.assertEqual(self.c['gates']['NATIVE_PROMOTION'],'FORBIDDEN')
    def test_fixture_coverage(self):
        self.assertEqual(len(self.cases),10)
        self.assertEqual(len({x['case_id'] for x in self.cases}),len(self.cases))
        self.assertTrue(set(self.c['inputs']['supported_kinds']).issubset({x['kind'] for x in self.cases}))
    def test_fixture_requirements(self):
        for item in self.cases:
            with self.subTest(case=item['case_id']):
                self.assertTrue(item['source_text'])
                self.assertTrue(item['illustrative_reference_fulltext'])
                self.assertTrue(item['assertions']['must_contain_any_language_concept'])
                self.assertTrue(item['assertions']['forbidden_assertions'])
                self.assertTrue(item['assertions']['no_mutation'])
                self.assertTrue(item['assertions']['authority_unchanged'])
    def test_manifest_source_integrity_evidence(self):
        self.assertEqual(self.s['manifest_source_hash_pass'],8)
        self.assertTrue(all(x['actual']==x['expected'] for x in self.s['manifest_files']))
        self.assertEqual(self.s['classification'],'HISTORICAL_SOURCE_NOT_CURRENT_EXECUTABLE_RUNTIME')
if __name__=='__main__': unittest.main(verbosity=2)
