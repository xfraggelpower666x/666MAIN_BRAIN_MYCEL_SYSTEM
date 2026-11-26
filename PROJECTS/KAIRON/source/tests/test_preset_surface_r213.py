import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import daemon_cli, portable

class PresetSurfaceTests(unittest.TestCase):
    def test_review_and_explicit_save(self):
        request={'device':'PC_SUNO_BROWSER','intent':{
            'motor':'rolling bass','mid':'acid','voice':'mantra',
            'structure':'drop and break','psychoacoustics':'orbit','bpm':144}}
        with tempfile.TemporaryDirectory() as root, patch.object(portable,'DATA',Path(root)):
            result=daemon_cli.preanalysis(request)
            self.assertTrue(result['context_preset']['preset_candidate'])
            self.assertIsNotNone(result['context_preset']['mandala_arrangement'])
            self.assertEqual(daemon_cli.preset_request({'preset_id':'test'})['versions'],[])
            payload={'preset_id':'test','analysis_request':request,'expected_version':0,
                     'review_sha256':result['preset_review_sha256']}
            with self.assertRaisesRegex(ValueError,'CREATOR_APPROVAL'):
                daemon_cli.preset_request(payload,save=True)
            with self.assertRaisesRegex(ValueError,'STALE_PRESET'):
                daemon_cli.preset_request(dict(payload,creator_approved=True,review_sha256='bad'),save=True)
            saved=daemon_cli.preset_request(dict(payload,creator_approved=True),save=True)
            self.assertEqual(saved['saved']['version'],1)
            self.assertEqual(daemon_cli.preset_request({'preset_id':'test'})['versions'],saved['versions'])

    def test_static_controls(self):
        html=daemon_cli.STATIC.read_text(encoding='utf-8')
        for marker in ('preset-consent','preset-history','mandala-view','forces-view','/api/preset/save'):
            self.assertIn(marker,html)
