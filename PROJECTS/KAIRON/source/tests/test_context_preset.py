import unittest
from engine.context_preset import evaluate

class ContextGatTests(unittest.TestCase):
    def seed(self, **kwargs):
        return dict(system_id='666TDI-001', lyrics='',story='',genre='Dark Psytrance',
            bpm=144,motor='',mid='',high='',atmosphere='',psychoacoustics='',structure='',ending='',voice='',**kwargs)
    def test_no_content(self):
        self.assertEqual(evaluate({'system_id':'666TDI-001'})['classification'],'REFERENCE_ONLY')
    def test_mantra_is_only_candidate(self):
        x=evaluate({'system_id':'666TDI-001','lyrics':'inner core mantra, orbit echo, one drop silence'})
        self.assertTrue(x['mandala_candidate'])
        self.assertFalse(x['preset_auto_save'])
    def test_full_candidate(self):
        x=evaluate({'system_id':'666TDI-001','genre':'Psytrance','motor':'rolling bass','mid':'acid 303','structure':'build and drop','voice':'vocal','ending':'final hit'})
        self.assertEqual(x['classification'],'PRESET_CANDIDATE')
        self.assertFalse(x['preset_candidate']['lyrics_embedded'])
    def test_simple_negative_not_positive(self):
        x=evaluate({'system_id':'666TDI-001','motor':'avoid rolling bass', 'mid':'without acid'})
        self.assertEqual(x['classification'],'TRACK_ONLY')
        self.assertFalse(x['signal_evidence']['MOTION'])
        self.assertFalse(x['signal_evidence']['FX'])
    def test_exclusion_reported(self):
        x=evaluate({'system_id':'666TDI-001','motor':'no rolling bass'})
        self.assertIn('rolling bass',x['negated_signals']['MOTION'])
    def test_voice_masking_hypothesis(self):
        x=evaluate({'system_id':'666TDI-001','lyrics':'vocal with acid'})
        self.assertIn('VOICE_FX_MASKING_RISK',[a['relation'] for a in x['functional_relations']])
        self.assertFalse(x['audio_measured'])
    def test_low_stability(self):
        x=evaluate({'system_id':'666TDI-001','motor':'rolling bass','high':'stereo orbit'})
        self.assertIn('LOW_STABILITY_VS_STEREO_MOVEMENT',[a['relation'] for a in x['functional_relations']])
    def test_foreign_identity(self):
        with self.assertRaisesRegex(ValueError,'FOREIGN_IDENTITY'): evaluate({'system_id':'LYVRA'})
    def test_bad_input(self):
        with self.assertRaisesRegex(ValueError,'INVALID_TRACK'): evaluate(None)
    def test_bad_fields(self):
        with self.assertRaisesRegex(ValueError,'INVALID_FIELD'): evaluate({'lyrics':[]})
    def test_cannot_install(self):
        x=evaluate({'lyrics':'vocal with acid, rolling bass, break and final hit'})
        self.assertFalse(x['module_auto_install'])
    def test_real_portable_analysis_consumer(self):
        import tempfile
        from pathlib import Path
        from engine import portable
        before=portable.DATA
        try:
            with tempfile.TemporaryDirectory() as work:
                portable.DATA=Path(work)
                track=portable.normalize({'title':'Proof','genre':'Dark Psytrance','bpm':144,'motor':'rolling bass','mid':'acid','high':'stereo orbit','energy':'controlled','lyrics':'inner core mantra, clear vocal','structure':'build, drop, silence','ending':'final hit'})
                track['track_id']='r209-consumer'
                result=portable.analyze(track)
                x=result['analysis']['context_preset']
                self.assertEqual(x['classification'],'PRESET_CANDIDATE')
                self.assertTrue(x['mandala_candidate'])
                self.assertFalse(x['preset_auto_save'])
        finally:
            portable.DATA=before
    def test_not_promoted_by_story(self):
        x=evaluate({'story':'we hear mantra and an echo with a drop'})
        self.assertIsNone(x['preset_candidate'])

if __name__=='__main__': unittest.main()
