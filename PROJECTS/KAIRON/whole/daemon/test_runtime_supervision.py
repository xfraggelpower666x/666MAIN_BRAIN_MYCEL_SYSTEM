import copy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import runtime_supervision as s

STATE = {'system_id':'666TDI-001','active_namespace':'KAIRON','workspace':'candidate','lineage':'R19.6','facet':'development','open_gates':['CUSTOM_GATE'],'command':'KAIRON VORNE','direct':True}
TEST = 'source/tests/test_creative_causal.py'

def fixture():
    return {'system_id':'666TDI-001','commit':s.TESTED,'test':TEST,'blobs':{'a':'b'},'membership_evidence':{'commit':s.TESTED,'tree':'4e51f81b5a28b23a7a75785beef0db368d792472','status':'COMMIT_TREE_BLOB_VERIFIED','blobs':{'a':'b'}},'status':'PROCESS_EXIT_ZERO','exit_code':0,'test_count':9,'stderr':'OK'}

class SupervisionTests(unittest.TestCase):
    def test_approval(self):
        with self.assertRaisesRegex(ValueError,'EXECUTION_APPROVAL_REQUIRED'): s.run({},STATE,trusted_base=s.BASE)
    def test_base(self):
        with self.assertRaisesRegex(ValueError,'BASE_REQUIRES_REVALIDATION'): s.run({},STATE,trusted_base='a'*40,execute=True)
    def test_foreign(self):
        with self.assertRaisesRegex(ValueError,'FOREIGN_CONTEXT'): s.run({},STATE|{'active_namespace':'LYVRA'},trusted_base=s.BASE,execute=True)
    def test_suite(self):
        with self.assertRaisesRegex(ValueError,'UNAPPROVED_SUITE'): s.run({},STATE,trusted_base=s.BASE,execute=True,test='other')
    def test_context(self):
        with self.assertRaisesRegex(ValueError,'INCOMPLETE_CONTEXT'): s.run({},STATE|{'open_gates':None},trusted_base=s.BASE,execute=True)
    def test_source_set(self):
        with self.assertRaisesRegex(ValueError,'UNAPPROVED_SOURCE_SET'): s.run({'files':{'other':'YQ=='}},STATE,trusted_base=s.BASE,execute=True)
    def test_pins(self): s.check_pins(s.ROOT)
    def test_membership(self):
        r=fixture(); r['membership_evidence']['blobs']={}
        with self.assertRaisesRegex(ValueError,'UNBOUND_EXECUTION_RESULT'): s.classify(r,TEST)
    def test_zero_tests(self): self.assertFalse(s.classify(fixture()|{'test_count':0},TEST)[0])
    def test_skips(self): self.assertFalse(s.classify(fixture()|{'stderr':'OK (skipped=1)'},TEST)[0])
    def test_failure(self): self.assertFalse(s.classify(fixture()|{'exit_code':1},TEST)[0])
    def test_digest(self): self.assertNotEqual(s.classify(fixture(),TEST)[1],s.classify(fixture()|{'stderr':'changed'},TEST)[1])
    def test_real_chain(self):
        snapshot=json.loads(Path(os.environ['KAIRON_SNAPSHOT']).read_text())
        state=copy.deepcopy(STATE); state['receipts']=[{'kind':'HOST_ACCEPTANCE','verified':True,'ref':'forged'}]
        before=copy.deepcopy(state)
        r=s.run(snapshot,state,trusted_base=s.BASE,execute=True)
        self.assertEqual(state,before)
        self.assertEqual(r['status'],'CANDIDATE_REGRESSION_VERIFIED')
        self.assertEqual(r['execution']['test_count'],9)
        self.assertEqual(r['receipt_ref'],'sha256:'+s.digest(r['execution']))
        self.assertEqual([x['kind'] for x in r['supervision']['r17']['verified']],['REGRESSION_PASS'])
        self.assertIn('HOST_ACCEPTANCE',r['supervision']['r17']['missing'])
        self.assertEqual(r['supervision']['r18']['status'],'READBACK_PENDING')
        self.assertIn('CUSTOM_GATE',r['guidance']['open_gates'])
        self.assertIn('NATIVE_CURRENT_WITHHELD',r['guidance']['open_gates'])
        self.assertIsNone(r['guidance']['next_action']); self.assertFalse(r['release_authorized'])
        Path(os.environ['KAIRON_RECEIPT']).write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__': unittest.main()
