import tempfile
import unittest
from pathlib import Path
from publish_resume import transfer, blob, git, PREFIX

class Resume(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        d=Path(self.tmp.name); self.remote=d/'remote'; self.work=d/'work'; self.root=d/'src'
        for p in (self.remote,self.work,self.root): p.mkdir()
        git(self.remote,'init','--bare'); git(self.work,'init')
        git(self.work,'config','user.name','Test'); git(self.work,'config','user.email','test@example.invalid')
        self.data={'mp3/a.py':b'a\r\n','boot/b.png':b'\x00\xff\x01','dj/c.log':b'private','restore/d.txt':b'text'}
        self.m={p:blob(b) for p,b in self.data.items()}
        for p,b in self.data.items():
            f=self.root/p; f.parent.mkdir(parents=True,exist_ok=True); f.write_bytes(b)
        f=self.work/(PREFIX+'mp3/a.py'); f.parent.mkdir(parents=True); f.write_bytes(self.data['mp3/a.py'])
        (self.work/'protected').write_text('keep'); git(self.work,'add','.'); git(self.work,'commit','-m','base')
        self.base=git(self.work,'rev-parse','HEAD').decode().strip()
        git(self.work,'push',str(self.remote),'HEAD:refs/heads/source')
    def approval(self,*paths):
        return {p:dict(sha=self.m[p],public_release=True,reviewer='synthetic test',evidence='fixture',privacy_review='PASS',rights_review='PASS') for p in paths}
    def go(self,head=None,allow=None,apply=True):
        return transfer(self.root,self.m,allow or {},head,remote=str(self.remote),base=self.base,source='refs/heads/source',target='refs/heads/target',apply=apply)
    def test_first_resume_and_idempotence(self):
        a=self.go(allow=self.approval('boot/b.png')); self.assertEqual(a['verified'],2)
        self.assertEqual(git(self.remote,'show','refs/heads/target:'+PREFIX+'boot/b.png'),self.data['boot/b.png'])
        b=self.go(a['commit'],self.approval('restore/d.txt')); self.assertEqual(b['verified'],3)
        self.assertEqual(git(self.remote,'rev-parse',b['backup']).decode().strip(),a['commit'])
        c=self.go(b['commit'],self.approval('restore/d.txt')); self.assertFalse(c['published']); self.assertEqual(c['held'],['dj/c.log'])
        self.assertEqual(git(self.remote,'show','refs/heads/target:protected'),b'keep')
    def test_dry(self):
        self.assertFalse(self.go(allow=self.approval('boot/b.png'),apply=False)['published'])
    def test_no_approval(self):
        self.assertFalse(self.go()['published'])
    def test_wrong_head(self):
        with self.assertRaises(ValueError): self.go('0'*40)
    def test_stale_head(self):
        self.go(allow=self.approval('boot/b.png'))
        with self.assertRaises(ValueError): self.go(allow=self.approval('restore/d.txt'))
    def test_wrong_approval_sha(self):
        a=self.approval('boot/b.png'); a['boot/b.png']['sha']='0'*40
        with self.assertRaises(ValueError): self.go(allow=a)
    def test_privacy_hold(self):
        a=self.approval('dj/c.log'); a['dj/c.log']['privacy_review']='HOLD'
        with self.assertRaises(ValueError): self.go(allow=a)
    def test_rights_hold(self):
        a=self.approval('boot/b.png'); a['boot/b.png']['rights_review']='HOLD'
        with self.assertRaises(ValueError): self.go(allow=a)
    def test_source_corruption(self):
        (self.root/'mp3/a.py').write_bytes(b'bad')
        with self.assertRaises(ValueError): self.go()
    def test_basis_change(self):
        (self.work/'protected').write_text('changed'); git(self.work,'commit','-am','bad')
        h=git(self.work,'rev-parse','HEAD').decode().strip(); git(self.work,'push',str(self.remote),'HEAD:refs/heads/target')
        with self.assertRaises(ValueError): self.go(h)
    def test_unrelated_history(self):
        git(self.work,'checkout','--orphan','alien'); git(self.work,'commit','--allow-empty','-m','alien')
        h=git(self.work,'rev-parse','HEAD').decode().strip(); git(self.work,'push',str(self.remote),'HEAD:refs/heads/target')
        with self.assertRaises(RuntimeError): self.go(h)

if __name__=='__main__': unittest.main()
