import tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engine'))
import worker
class TestWorker(unittest.TestCase):
 def test_profile_set(self):self.assertEqual(set(worker.PROFILES),{'stream','dj','custom'})
 def test_existing_file_protection(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'track.mp3').write_bytes(b'KEEP')
   self.assertEqual(worker.destination(p/'track.wav',p).name,'track_1.mp3')
   self.assertEqual((p/'track.mp3').read_bytes(),b'KEEP')
 def test_empty_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):worker.validate({'files':[],'output':d})
 def test_invalid_profile(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);f=p/'file.wav';f.write_bytes(b'x')
   with self.assertRaises(ValueError):worker.validate({'files':[str(f)],'output':d,'profile':'bad'})
