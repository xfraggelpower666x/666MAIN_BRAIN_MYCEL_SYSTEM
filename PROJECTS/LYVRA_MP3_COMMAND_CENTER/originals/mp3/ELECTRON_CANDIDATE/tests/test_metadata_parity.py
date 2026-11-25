import hashlib, json, subprocess, tempfile, unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORKER=ROOT/'engine_bridge.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(request):
 p=subprocess.run([sys.executable,'-u',str(WORKER)],input=json.dumps(request)+'\n',text=True,capture_output=True,timeout=40)
 msgs=[json.loads(x) for x in p.stdout.splitlines() if x.strip()]
 return p,msgs
class MetadataParity(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=tempfile.TemporaryDirectory();cls.root=Path(cls.d.name)
  cls.source=cls.root/'Original Music.mp3'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','lavfi','-i','sine=frequency=440:duration=1','-codec:a','libmp3lame','-b:a','320k',str(cls.source)],check=True,timeout=20)
 @classmethod
 def tearDownClass(cls):cls.d.cleanup()
 def test_copy_verified_and_original_unchanged(self):
  target=self.root/'edited.mp3';before=sha(self.source)
  p,msgs=run({'action':'metadata_copy','source':str(self.source),'destination':str(target),'fields':{'TIT2':'My Title','TPE1':'DJ','TALB':'Sound Design'}})
  self.assertEqual(p.returncode,0,msgs)
  self.assertEqual(sha(self.source),before)
  self.assertTrue(any(x.get('data',{}).get('verified')=='ID3_READBACK_PASS' for x in msgs))
  self.assertEqual(__import__('mutagen.id3',fromlist=['ID3']).ID3(target)['TIT2'].text[0],'My Title')
  again,reply=run({'action':'metadata_copy','source':str(self.source),'destination':str(target),'fields':{'TIT2':'overwrite'}})
  self.assertNotEqual(again.returncode,0)
  self.assertEqual(__import__('mutagen.id3',fromlist=['ID3']).ID3(target)['TIT2'].text[0],'My Title')
 def test_invalid_and_self_copy_fail_closed(self):
  before=sha(self.source)
  for fields in ({'TIT2':23},{'NOPE':'x'},{'TIT2':'a'*2049}):
   p,msgs=run({'action':'metadata_copy','source':str(self.source),'destination':str(self.root/'invalid.mp3'),'fields':fields})
   self.assertNotEqual(p.returncode,0)
   self.assertFalse((self.root/'invalid.mp3').exists())
  p,msgs=run({'action':'metadata_copy','source':str(self.source),'destination':str(self.source),'fields':{'TIT2':'overwrite'}})
  self.assertNotEqual(p.returncode,0)
  self.assertEqual(sha(self.source),before)
if __name__=='__main__':unittest.main()
