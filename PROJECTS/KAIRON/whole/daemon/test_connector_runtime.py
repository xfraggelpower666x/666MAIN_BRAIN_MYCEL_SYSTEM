"""Focused R19.6 tests: actual bridge dispatch plus fail-closed acquisition."""
import copy
import unittest
from pathlib import Path
from connector_runtime import BRIDGE, acquire, execute_native, raw_tree
from execution_trust import oid


def fixture():
    import execution_bridge
    files = {BRIDGE:Path(execution_bridge.__file__).read_bytes(), 'test_native.py':b'import unittest\nclass T(unittest.TestCase):\n def test_real(self): self.assertEqual(2+2,4)\n'}
    trees = {}
    def tree(entries):
        raw = b''.join(m.lstrip('0').encode()+b' '+n.encode()+b'\0'+bytes.fromhex(s) for n,m,s in entries)
        sha = oid('tree',raw)
        trees[sha] = {'sha':sha,'truncated':False,'entries':entries}
        return sha
    leaf = tree([['execution_bridge.py','100644',oid('blob',files[BRIDGE])]])
    whole = tree([['daemon','040000',leaf]])
    project = tree([['test_native.py','100644',oid('blob',files['test_native.py'])],['whole','040000',whole]])
    root = tree([['PROJECTS','040000',tree([['KAIRON','040000',project]])]])
    raw = (f'tree {root}\nauthor Fixture <fixture@example.invalid> 0 +0000\ncommitter Fixture <fixture@example.invalid> 0 +0000\n\nfixture\n').encode()
    head = oid('commit',raw)
    who = {'name':'Fixture','email':'fixture@example.invalid','date':'1970-01-01T00:00:00Z'}
    commit = {'sha':head,'tree':root,'parents':[],'author':who,'committer':who,'message':'fixture','verification':{'reason':'unsigned'}}
    return files,trees,commit,head


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.files,self.trees,self.commit,self.head = fixture()
    def git(self,kind,sha):
        return self.commit if kind=='commit' else self.trees[sha]
    def file(self,path,head):
        return self.files[path]
    def args(self):
        return dict(trusted_head=self.head,paths=list(self.files),test='test_native.py',execute=True)
    def acquire(self,**changes):
        return acquire(self.git,self.file,**(self.args()|changes))
    def test_actual_execution(self):
        r=execute_native(self.git,self.file,**self.args())
        self.assertEqual((r['status'],r['test_count']),('PROCESS_EXIT_ZERO',1))
        self.assertEqual(r['membership_evidence']['status'],'COMMIT_TREE_BLOB_VERIFIED')
        self.assertFalse(r['production_release'])
    def test_approval_required(self):
        with self.assertRaisesRegex(ValueError,'EXECUTION_APPROVAL_REQUIRED'): self.acquire(execute=False)
    def test_head_mismatch(self):
        with self.assertRaisesRegex(ValueError,'HEAD_MISMATCH'): self.acquire(trusted_head='a'*40)
    def test_commit_tamper(self):
        self.commit['message']='changed'
        with self.assertRaisesRegex(ValueError,'COMMIT_RAW_HASH_MISMATCH'): self.acquire()
    def test_tree_tamper(self):
        self.trees[self.commit['tree']]['entries'][0][0]='OTHER'
        with self.assertRaisesRegex(ValueError,'TREE_RAW_HASH_MISMATCH'): self.acquire()
    def test_truncated_tree(self):
        self.trees[self.commit['tree']]['truncated']=True
        with self.assertRaisesRegex(ValueError,'TREE_INCOMPLETE_OR_MISMATCH'): self.acquire()
    def test_blob_tamper(self):
        self.files['test_native.py']=b'changed'
        with self.assertRaisesRegex(ValueError,'BLOB_NOT_IN_COMMIT'): self.acquire()
    def test_path_traversal(self):
        with self.assertRaisesRegex(ValueError,'INVALID_PATH'): self.acquire(paths=list(self.files)+['../test_native.py'])
    def test_missing_bridge(self):
        with self.assertRaisesRegex(ValueError,'REQUIRED_PATH_OR_DUPLICATE'): self.acquire(paths=['test_native.py'])
    def test_duplicate_path(self):
        with self.assertRaisesRegex(ValueError,'REQUIRED_PATH_OR_DUPLICATE'): self.acquire(paths=list(self.files)*2)
    def test_signed_commit_not_silently_reconstructed(self):
        self.commit['verification']['reason']='valid'
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_COMMIT_FORMAT'): self.acquire()


if __name__ == '__main__':
    unittest.main()
