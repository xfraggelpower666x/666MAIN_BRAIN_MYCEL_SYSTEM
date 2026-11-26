import sys,unittest
sys.path.insert(0,'src')
from music_arch import *
class ArchTests(unittest.TestCase):
    def setUp(self):
        self.i=MusicalIntent(title='Orbit',genre='Dark Psytrance',bpm=145,motor='straight 16th mono psybass',mid='acid',high='spectral orbit',atmosphere='void',energy='high',lyrics='my original line',avoid='pop, bounce',target_seconds=340)
    def test_source_unchanged(self):
        before=asdict(self.i);compile_intent(self.i,'lyria2_asg');self.assertEqual(before,asdict(self.i))
    def test_budget(self):
        r=compile_intent(self.i,'lyria2_asg');self.assertLessEqual(len(r['fields']['description']),400);self.assertLessEqual(len(r['fields']['negative']),100)
    def test_duration_warning(self):
        self.assertIn('DURATION_EXCEEDS_HISTORICAL_RENDERER_LIMIT',compile_intent(self.i,'ace_step_asg')['warnings'])
    def test_no_silent_loss(self):
        self.i.motor='x'*500
        r=compile_intent(self.i,'lyria2_asg');self.assertTrue(any(x['field']=='motor' for x in r['omissions']))
    def test_no_invented_limits(self):
        self.assertIsNone(SPECS['asg_main']['fields']['style'])
    def test_source_lyrics(self):
        self.assertEqual(compile_intent(self.i,'ace_step_asg')['fields']['lyrics'],self.i.lyrics)
if __name__=='__main__': unittest.main()
