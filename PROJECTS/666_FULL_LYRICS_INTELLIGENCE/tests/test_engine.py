import sys,tempfile,unittest,zipfile,json,sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engine'))
import bridge
class EngineTests(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.base=Path(self.t.name);self.c=bridge.dbconnect(self.base)
 def tearDown(self):self.c.close();self.t.cleanup()
 def test_split_120_song_titles(self):
  text='\n'.join(f'Title: Track {i}\nLyrics:\n[Verse]\nThis is song {i} that goes along\n' for i in range(120))
  p=self.base/'giant.md';p.write_text(text)
  r=bridge.importer(self.c,self.base,{'paths':[str(p)]});self.assertEqual(r['inserted'],120);self.assertEqual(self.c.execute('select count(*) from records').fetchone()[0],120)
  idx=json.loads((self.base/'index'/'index.json').read_text());self.assertEqual(idx['total'],120)
 def test_duplicate_idempotent(self):
  p=self.base/'lyrics.txt';p.write_text('Lyrics:\n[Verse]\nBeautiful moon in quiet light')
  a=bridge.importer(self.c,self.base,{'paths':[str(p)]});b=bridge.importer(self.c,self.base,{'paths':[str(p)]});self.assertEqual(a['inserted'],1);self.assertEqual(b['skipped'],1)
 def test_chat_export(self):
  source={'mapping':{'a':{'message':{'author':{'role':'user'},'content':{'parts':['LYVRA SYSTEMSTART\nThis is a message about architecture.']}}},'b':{'message':{'author':{'role':'assistant'},'content':{'parts':['This prompt discusses 666TDH design and tests.']}}}}}
  p=self.base/'chat.json';p.write_text(json.dumps(source));r=bridge.importer(self.c,self.base,{'paths':[str(p)]});self.assertEqual(r['inserted'],2)
 def test_zip_mixed(self):
  p=self.base/'backup.zip'
  with zipfile.ZipFile(p,'w') as z:z.writestr('songs/a.md','Lyrics:\n[Verse]\nOne more song from the deep');z.writestr('../bad.txt','bad');z.writestr('unknown.xyz','xxxx')
  r=bridge.importer(self.c,self.base,{'paths':[str(p)]});self.assertEqual(r['inserted'],1);self.assertTrue(any('Unsicherer' in w for w in r['warnings']))
 def test_archive_and_readback(self):
  p=self.base/'x.txt';p.write_text('Lyrics:\n[Verse]\nThis music will be kept forever')
  bridge.importer(self.c,self.base,{'paths':[str(p)]});id=self.c.execute('select id from records').fetchone()[0]
  r=bridge.archive(self.c,self.base,{'ids':[id]});self.assertTrue(Path(r['path']).exists());self.assertEqual(self.c.execute('select archived from records where id=?',(id,)).fetchone()[0],1)
  with zipfile.ZipFile(r['path']) as z:self.assertTrue('index.json' in z.namelist())
 def test_unknown_format_registered(self):
  p=self.base/'secret.bin';p.write_bytes(b'1234');r=bridge.importer(self.c,self.base,{'paths':[str(p)]});self.assertEqual(r['sources'][0]['status'],'unextracted');self.assertEqual(self.c.execute('select count(*) from records').fetchone()[0],0)
 def test_export_index(self):
  p=self.base/'a.md';p.write_text('Lyrics:\n[Chorus]\nEndless sonic green neon sky');bridge.importer(self.c,self.base,{'paths':[str(p)]});r=bridge.export_records(self.c,self.base,{'format':'zip'});self.assertEqual(r['count'],1)
  with zipfile.ZipFile(r['path']) as z:self.assertIsNone(z.testzip())
 def test_legacy_readonly(self):
  db=Path(__file__).resolve().parents[1]/'legacy_r02'/'app'/'lyrics_library.db'
  r=bridge.migrate(self.c,self.base,{'path':str(db)});self.assertEqual(r['legacy_count'],1915);self.assertGreaterEqual(r['inserted'],1800)
  self.assertEqual(sqlite3.connect(str(db)).execute('select count(*) from lyrics').fetchone()[0],1915)
 def test_project_routing(self):
  p,alternatives=bridge.project_for('LYVRA track development and Suno','some.txt');self.assertEqual(p,'LYVRA')
 def test_empty(self):self.assertEqual(bridge.stats(self.c)['total'],0)
if __name__=='__main__':unittest.main()
