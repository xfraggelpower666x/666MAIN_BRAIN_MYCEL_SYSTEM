import sys,tempfile,unittest,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engine'))
import bridge,reconciliation
class ReconciliationTests(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.base=Path(self.t.name);self.c=bridge.dbconnect(self.base)
 def tearDown(self):self.c.close();self.t.cleanup()
 def test_empty(self):
  r=reconciliation.summarize(self.base/'catalog.sqlite','LYVRA')
  self.assertEqual(r['catalog']['records'],0);self.assertEqual(r['reference']['status'],'NO_REFERENCE')
 def test_counts(self):
  p=self.base/'song.txt';p.write_text('LYVRA Lyrics:\n[Chorus]\nThe night is blue and alive')
  bridge.importer(self.c,self.base,{'paths':[str(p)]})
  r=reconciliation.summarize(self.base/'catalog.sqlite','LYVRA')
  self.assertEqual(r['catalog']['records'],1);self.assertEqual(r['comparison']['outcome'],'REVIEW_REQUIRED')
 def test_hash_not_authority(self):
  f=self.base/'current.json';f.write_text(json.dumps({'project':'LYVRA','branch':'lyvra'}))
  sha=hashlib.sha256(f.read_bytes()).hexdigest();r=reconciliation.summarize(self.base/'catalog.sqlite','LYVRA',f,sha)
  self.assertEqual(r['reference']['status'],'CANDIDATE_HASH_MATCHED');self.assertEqual(r['reference']['native_authority'],'NOT_VERIFIED')
 def test_hash_conflict(self):
  f=self.base/'current.json';f.write_text('{}');r=reconciliation.summarize(self.base/'catalog.sqlite','LYVRA',f,'0'*64)
  self.assertEqual(r['reference']['status'],'HASH_CONFLICT')
if __name__=='__main__':unittest.main()
