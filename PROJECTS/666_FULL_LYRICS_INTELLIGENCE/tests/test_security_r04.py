import os,sys,zipfile,tempfile,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engine'))
import bridge
class SecurityR04(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.base=Path(self.t.name);self.c=bridge.dbconnect(self.base)
 def tearDown(self):self.c.close();self.t.cleanup()
 def test_zip_drive_path_rejected(self):
  p=self.base/'drive.zip'
  with zipfile.ZipFile(p,'w') as z:z.writestr('C:/sneaky.md','Lyrics:\n[Verse]\nSecret123 data song')
  res=bridge.importer(self.c,self.base,{'paths':[str(p)]})
  self.assertEqual(res['inserted'],0);self.assertTrue(any('Unsicherer' in w for w in res['warnings']))
 def test_zip_entry_is_bounded(self):
  p=self.base/'large.zip'
  with zipfile.ZipFile(p,'w',zipfile.ZIP_STORED) as z:z.writestr('giant.txt','x'*(bridge.MAX_FILE+1))
  res=bridge.importer(self.c,self.base,{'paths':[str(p)]})
  self.assertEqual(res['inserted'],0);self.assertTrue(any('ZIP-Limit' in w for w in res['warnings']))
 def test_missing_file_reports_error_no_db_mutation(self):
  res=bridge.importer(self.c,self.base,{'paths':[str(self.base/'MISSING.txt')]})
  self.assertEqual(res['sources'][0]['status'],'error');self.assertEqual(bridge.stats(self.c)['total'],0)
 def test_archive_unknown_id_is_failure(self):
  with self.assertRaises(ValueError):bridge.archive(self.c,self.base,{'ids':['nonexistent-id']})
  self.assertEqual(bridge.stats(self.c)['archived'],0)
 def test_archive_duplicate_id_handled(self):
  p=self.base/'lyric.txt';p.write_text('Lyrics:\n[Verse]\nA neon dream beyond the stars')
  bridge.importer(self.c,self.base,{'paths':[str(p)]});rid=self.c.execute('select id from records').fetchone()[0]
  r=bridge.archive(self.c,self.base,{'ids':[rid,rid]})
  self.assertEqual(r['archived'],1)
 def test_bad_input_count_rejected(self):
  with self.assertRaises(ValueError):bridge.importer(self.c,self.base,{'paths':['f']*201})
 def test_json_record_and_index(self):
  p=self.base/'song.md';p.write_text('Title: Demo\nLyrics:\n[Verse]\nLittle waves and endless light')
  r=bridge.importer(self.c,self.base,{'paths':[str(p)]});self.assertEqual(r['inserted'],1)
  rid=self.c.execute('select id from records').fetchone()[0]
  self.assertEqual(json.loads((self.base/'index/index.json').read_text())['total'],1)
  self.assertTrue(list((self.base/'records').rglob(rid+'.json')))
if __name__=='__main__':unittest.main()
