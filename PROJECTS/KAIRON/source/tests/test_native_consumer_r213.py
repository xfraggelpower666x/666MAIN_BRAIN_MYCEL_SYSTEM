"""R21.3 native consumer integration regression."""
import json
import tempfile
import unittest
from pathlib import Path
from engine import portable as p

class NativeConsumerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        original=p.DATA
        self.addCleanup(setattr,p,'DATA',original)
        p.DATA=Path(self.tmp.name)
        self.intent=json.loads((p.ROOT/'examples'/'intent.json').read_text())

    def test_native_reports_consumed(self):
        out=p.analyze(p.create_track(self.intent))
        a=out['analysis']
        self.assertEqual(a['musical_forces'],a['preanalysis']['musical_forces'])
        self.assertFalse(a['preanalysis']['audio_verified'])
        self.assertFalse(a['music_memory']['automatic_promotion'])
        self.assertNotIn('prompt_history',a['music_memory'])
        self.assertEqual(a['music_memory']['relations'],[])

    def test_invalid_context_rejected(self):
        track=p.create_track(dict(self.intent,music_context='invalid'))
        with self.assertRaisesRegex(ValueError,'INVALID_MUSIC_CONTEXT'):
            p.analyze(track)

if __name__=='__main__':
    unittest.main()
