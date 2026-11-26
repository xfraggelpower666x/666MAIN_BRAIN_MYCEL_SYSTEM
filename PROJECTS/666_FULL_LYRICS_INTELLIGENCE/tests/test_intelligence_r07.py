"""R07 isolated Python regression, no user data."""
import unittest,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
import bridge
from intelligence import metrics,analyze_record,compare_records,project_insights
class R07Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.conn=bridge.dbconnect(self.base)
 def tearDown(self):self.conn.close();self.tmp.cleanup()
 def seed(self,text):
  _,rid=bridge.insert(self.conn,"LYRICS_R07","lyrics","Example",text,"fixture.txt","fixturehash",1.0,["music"]);self.conn.commit();return rid
 def test_repeats_sections(self):
  result=metrics("[Verse]\nNeon electric rain\nNeon electric rain\n[Chorus]\nDark pressure")
  self.assertEqual(result["section_count"],2);self.assertEqual(result["repeat_lines"][0]["count"],2)
 def test_empty(self):self.assertEqual(metrics("")["word_count"],0)
 def test_read_only(self):
  txt="[Hook]\nNeon pulse\nNeon pulse";rid=self.seed(txt)
  self.assertEqual(analyze_record(self.conn,rid)["metrics"]["repeat_lines"][0]["count"],2)
  self.assertEqual(self.conn.execute("SELECT content FROM records WHERE id=?",(rid,)).fetchone()[0],txt)
 def test_compare(self):
  a=self.seed("Neon pressure forever");b=self.seed("Dark neon pressure")
  self.assertEqual(len(compare_records(self.conn,[a,b])["items"]),2)
  with self.assertRaises(ValueError):compare_records(self.conn,[a,a])
 def test_project(self):
  self.seed("One text entry");self.assertEqual(project_insights(self.conn)[0]["active"],1)
if __name__=="__main__":unittest.main()
