import pathlib,tempfile,unittest,subprocess,sys
from publish_originals import transfer,blob,PREFIX
class Bulk(unittest.TestCase):
 def test_transfer(self):
  with tempfile.TemporaryDirectory() as d:
   d=pathlib.Path(d); remote=d/'remote.git';work=d/'work';src=d/'src';src.mkdir();remote.mkdir();work.mkdir()
   def git(r,*a): return subprocess.check_output(['git','-C',str(r),*a],stderr=subprocess.DEVNULL).decode().strip()
   git(remote,'init','--bare');git(work,'init');git(work,'config','user.name','Test');git(work,'config','user.email','test@example.invalid');git(work,'config','core.autocrlf','false')
   files={'mp3/a.py':b'a\r\n','boot/b.webp':b'\x00\xff\x01','dj/c.txt':b'hello'};m={p:blob(b) for p,b in files.items()}
   for p,b in files.items(): f=src/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
   f=work/(PREFIX+'mp3/a.py');f.parent.mkdir(parents=True);f.write_bytes(files['mp3/a.py']);(work/'unrelated').write_text('protected');git(work,'add','.');git(work,'commit','-m','base');base=git(work,'rev-parse','HEAD');git(work,'push',str(remote),'HEAD:refs/heads/source')
   args=(src,m,str(remote),base,'refs/heads/source','refs/heads/target','refs/heads/backup')
   dry=transfer(*args);self.assertFalse(dry['published']);self.assertEqual(dry['missing'],2)
   result=transfer(*args,apply=True);self.assertEqual(result['verified'],3);self.assertEqual(git(remote,'rev-parse','refs/heads/source'),base);self.assertEqual(git(remote,'rev-parse','refs/heads/backup'),base);self.assertEqual(git(remote,'show','refs/heads/target:unrelated'),'protected')
   with self.assertRaises(ValueError):transfer(*args,apply=True)
   (src/'mp3/a.py').write_bytes(b'changed');self.assertRaises(ValueError,transfer,*args)
if __name__=='__main__':unittest.main()
