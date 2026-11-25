import tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engine'))
import playlist
class PlaylistTests(unittest.TestCase):
 def test_creates_relative_m3u(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);a=p/'track.mp3';a.write_bytes(b'audio')
   output=playlist.export_m3u(p,[a]);self.assertEqual(output.read_text(encoding='utf-8'),'#EXTM3U\ntrack.mp3\n')
 def test_existing_preserved(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);a=p/'track.mp3';a.write_bytes(b'audio');(p/'AUTO_DJ_EXPORT.m3u').write_text('old')
   output=playlist.export_m3u(p,[a]);self.assertEqual(output.name,'AUTO_DJ_EXPORT_1.m3u')
   self.assertEqual((p/'AUTO_DJ_EXPORT.m3u').read_text(),'old')
 def test_invalid_path(self):
  with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
   song=Path(b)/'x.mp3';song.write_bytes(b'mp3')
   with self.assertRaises(ValueError):playlist.export_m3u(Path(a),[song])
 def test_reject_invalid_name(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):playlist.safe_playlist_path(d,'../escape')
