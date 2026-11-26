import base64
import copy
import unittest
from execution_trust import oid, verify_bundle, run_verified
from unittest.mock import patch
import sys
from types import SimpleNamespace

def fixture():
    objects = {}
    def obj(kind, raw):
        key = oid(kind, raw)
        objects[key] = base64.b64encode(raw).decode()
        return key
    data = b'import unittest\n'
    blob = oid('blob', data)
    leaf = obj('tree', b'100644 test_demo.py\0' + bytes.fromhex(blob))
    for name in (b'KAIRON', b'PROJECTS'):
        leaf = obj('tree', b'40000 ' + name + b'\0' + bytes.fromhex(leaf))
    head = obj('commit', ('tree '+leaf+'\n\nfixture\n').encode())
    bundle = dict(commit=head, system_id='666TDI-001', namespace='KAIRON', scope='PROJECTS/KAIRON/', test='test_demo.py', execute=True, files=[dict(path='test_demo.py', sha=blob, base64=base64.b64encode(data).decode())])
    return bundle, objects, head

class TrustTests(unittest.TestCase):
    def setUp(self): self.b,self.o,self.h=fixture()
    def verify(self): return verify_bundle(self.b,self.o,trusted_head=self.h)
    def test_valid(self): self.assertEqual(self.verify()['status'],'COMMIT_TREE_BLOB_VERIFIED')
    def test_head(self):
        self.b['commit']='a'*40
        with self.assertRaisesRegex(ValueError,'HEAD_MISMATCH'): self.verify()
    def test_commit_tamper(self):
        self.o[self.h]=base64.b64encode(b'tampered').decode()
        with self.assertRaisesRegex(ValueError,'OBJECT_HASH_MISMATCH'): self.verify()
    def test_missing_tree(self):
        self.o={self.h:self.o[self.h]}
        with self.assertRaisesRegex(ValueError,'OBJECT_MISSING'): self.verify()
    def test_forged_blob(self):
        self.b['files'][0].update(sha=oid('blob',b'other'),base64='b3RoZXI=')
        with self.assertRaisesRegex(ValueError,'BLOB_NOT_IN_COMMIT'): self.verify()
    def test_path(self):
        self.b['files'][0]['path']='not_present.py'
        with self.assertRaisesRegex(ValueError,'PATH_NOT_IN_COMMIT'): self.verify()
    def test_foreign(self):
        self.b['scope']='PROJECTS/LYVRA/'
        with self.assertRaisesRegex(ValueError,'FOREIGN_SCOPE'): self.verify()
    def test_traversal(self):
        self.b['files'][0]['path']='../test_demo.py'
        with self.assertRaisesRegex(ValueError,'INVALID_PATH'): self.verify()
    def test_duplicate(self):
        self.b['files']*=2
        with self.assertRaisesRegex(ValueError,'DUPLICATE_PATH'): self.verify()
    def test_dispatch_gate(self):
        calls=[]
        with patch.dict(sys.modules, {'execution_bridge':SimpleNamespace(run=lambda b: calls.append(b) or {'status':'NO_TESTS_EXECUTED'})}):
            self.assertEqual(run_verified(self.b,self.o,trusted_head=self.h)['status'],'NO_TESTS_EXECUTED')
            self.b['commit']='a'*40
            with self.assertRaises(ValueError): run_verified(self.b,self.o,trusted_head=self.h)
        self.assertEqual(len(calls),1)

class RealGitTests(unittest.TestCase):
    def test_real_git_object_membership(self):
        import subprocess, tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            def git(*args):
                return subprocess.check_output(['git','-C',tmp,*args],stderr=subprocess.DEVNULL)
            git('init','-q'); git('config','user.email','fixture@example.invalid'); git('config','user.name','Fixture')
            path=Path(tmp)/'PROJECTS/KAIRON/test_demo.py'; path.parent.mkdir(parents=True)
            data=b'import unittest\n'; path.write_bytes(data)
            git('add','.'); git('commit','-qm','fixture')
            head=git('rev-parse','HEAD').decode().strip(); objects={}
            def collect(key,kind):
                raw=git('cat-file',kind,key); objects[key]=base64.b64encode(raw).decode(); return raw
            tree=collect(head,'commit').splitlines()[0][5:].decode()
            from execution_trust import tree_entries
            for part in (b'PROJECTS',b'KAIRON',b'test_demo.py'):
                _, tree=tree_entries(collect(tree,'tree'))[part]
            b,_,_=fixture(); b['commit']=head; b['files'][0]['sha']=tree
            self.assertEqual(verify_bundle(b,objects,trusted_head=head)['blobs']['test_demo.py'],tree)

if __name__ == "__main__": unittest.main()
