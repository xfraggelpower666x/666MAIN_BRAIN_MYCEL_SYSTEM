import unittest, zipfile
import test_publish_resume
from controlled_release import release
from binary_readback import verify
from asset_review import inspect
from PIL import Image
from publish_resume import blob

class Integrated(unittest.TestCase):
    def setUp(self):
        self.f=test_publish_resume.Resume(); self.f.setUp(); self.addCleanup(self.f.doCleanups)
        f=self.f; p='boot/b.png'; Image.new('RGB',(2,2)).save(f.root/p); f.data[p]=(f.root/p).read_bytes(); f.m[p]=blob(f.data[p]); self.p=p
        self.archives={}
        for domain in ('boot','dj'):
            z=f.root/(domain+'.zip'); self.archives[domain]=z
            with zipfile.ZipFile(z,'w') as a:
                for path,b in f.data.items():
                    if path.startswith(domain+'/'): a.writestr(path.split('/',1)[1],b)
        self.matrix=inspect(f.root,f.m,self.archives,[p,'dj/c.log'])
        self.opt=dict(remote=str(f.remote),base=f.base,source='refs/heads/source',target='refs/heads/target')
    def go(self,allow,head=None,apply=True):
        return release(self.f.root,self.f.m,self.archives,self.matrix,allow,head,apply=apply,**self.opt)
    def allow(self,p):
        a=self.f.approval(p); a[p]['sha256']=self.matrix[p]['sha256']; return a
    def test_binary_end_to_end(self):
        a=self.go(self.allow(self.p)); self.assertEqual(a['independent_readback']['files'][self.p]['sha256'],self.matrix[self.p]['sha256']); self.assertEqual(a['verified'],2)
        self.assertFalse(self.go(self.allow(self.p),a['commit'])['published'])
    def test_no_approval(self): self.assertFalse(self.go({})['published'])
    def test_stale_review(self):
        self.matrix[self.p]['bytes']=0
        with self.assertRaises(ValueError): self.go(self.allow(self.p))
    def test_approval_hash(self):
        a=self.allow(self.p); a[self.p]['sha256']='wrong'
        with self.assertRaises(ValueError): self.go(a)
    def test_wrong_head(self):
        a=self.go(self.allow(self.p))
        with self.assertRaises(ValueError): verify(self.opt['remote'],self.opt['target'],self.f.base,self.f.m,[self.p])
    def test_unknown_path(self):
        with self.assertRaises(ValueError): verify(self.opt['remote'],self.opt['source'],self.f.base,self.f.m,['unknown'])
    def test_sensitive_log(self):
        p='dj/c.log'; data=b'C:\\Users\\synthetic\\file'; (self.f.root/p).write_bytes(data); self.f.m[p]=blob(data)
        with zipfile.ZipFile(self.archives['dj'],'w') as z: z.writestr('c.log',data)
        self.matrix.update(inspect(self.f.root,self.f.m,self.archives,[p]))
        with self.assertRaisesRegex(ValueError,'Sensitive original log'): self.go(self.allow(p))
    def test_missing_review(self):
        a=self.allow(self.p); del self.matrix[self.p]
        with self.assertRaisesRegex(ValueError,'Missing asset review'): self.go(a)
