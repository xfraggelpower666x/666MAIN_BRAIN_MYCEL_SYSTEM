import base64
import unittest
from execution_bridge import blob, run


def bundle(code=b'import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n'):
    return dict(system_id='666TDI-001', namespace='KAIRON', scope='PROJECTS/KAIRON/', commit='a'*40, execute=True, test='test_sample.py', files=[dict(path='test_sample.py', base64=base64.b64encode(code).decode(), sha=blob(code))])


class BridgeTests(unittest.TestCase):
    def test_success(self):
        r=run(bundle()); self.assertEqual(r['exit_code'],0); self.assertIn('Ran 1 test',r['stderr']); self.assertFalse(r['production_release'])
    def test_failure(self):
        r=run(bundle(b'import unittest\nclass T(unittest.TestCase):\n def test_bad(self): self.fail()\n')); self.assertNotEqual(r['exit_code'],0); self.assertEqual(r['status'],'REGRESSION_FAILED')
    def test_hash(self):
        b=bundle(); b['files'][0]['sha']='0'*40
        with self.assertRaisesRegex(ValueError,'BLOB_MISMATCH'): run(b)
    def test_traversal(self):
        b=bundle(); b['files'][0]['path']='../test_sample.py'
        with self.assertRaisesRegex(ValueError,'INVALID_PATH'): run(b)
    def test_scope(self):
        b=bundle(); b['scope']='PROJECTS/LYVRA/'
        with self.assertRaisesRegex(ValueError,'FOREIGN_SCOPE'): run(b)
    def test_approval(self):
        b=bundle(); b['execute']=False
        with self.assertRaisesRegex(ValueError,'EXECUTION_APPROVAL_REQUIRED'): run(b)
    def test_duplicate(self):
        b=bundle(); b['files']*=2
        with self.assertRaisesRegex(ValueError,'DUPLICATE_PATH'): run(b)
    def test_unbound(self):
        b=bundle(); b['test']='test_missing.py'
        with self.assertRaisesRegex(ValueError,'TEST_NOT_BOUND'): run(b)

if __name__=='__main__': unittest.main()
