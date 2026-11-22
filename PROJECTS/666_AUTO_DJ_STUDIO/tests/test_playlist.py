"""Read-only functional regressions for additive M3U export."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
MOD=Path(__file__).resolve().parents[1]/"engine"/"playlist.py"
spec=importlib.util.spec_from_file_location("playlist",MOD)
playlist=importlib.util.module_from_spec(spec);spec.loader.exec_module(playlist)
class PlaylistTests(unittest.TestCase):
    def test_creates_relative_m3u(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);a=p/"track.mp3";a.write_bytes(b"audio")
            result=playlist.export_m3u(p,[a])
            self.assertEqual(result.read_text(encoding="utf-8"),"#EXTM3U\ntrack.mp3\n")
    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);a=p/"track.mp3";a.write_bytes(b"audio")
            (p/"AUTO_DJ_EXPORT.m3u").write_text("old")
            result=playlist.export_m3u(p,[a])
            self.assertEqual(result.name,"AUTO_DJ_EXPORT_1.m3u")
            self.assertEqual((p/"AUTO_DJ_EXPORT.m3u").read_text(),"old")
    def test_no_source_outside_output(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            p=Path(d);a=Path(elsewhere)/"track.mp3";a.write_bytes(b"audio")
            with self.assertRaises(ValueError):playlist.export_m3u(p,[a])
    def test_no_missing_tracks(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):playlist.export_m3u(Path(d),[Path(d)/"missing.mp3"])
    def test_no_empty_export(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):playlist.export_m3u(Path(d),[])
    def test_name_guard(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):playlist.safe_playlist_path(Path(d),"../escape")
if __name__=="__main__":unittest.main()
