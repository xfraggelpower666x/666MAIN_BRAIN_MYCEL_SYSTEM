"""Real loopback HTTP acceptance; no production data or external calls."""
import concurrent.futures
import importlib
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import portable, preset_evidence

# Reuse the existing HTTP harness without re-registering its test class.
Harness=importlib.import_module('test_daemon_http_guard').DaemonHttpGuardTests

class PresetHttpTests(unittest.TestCase):
    setUp=Harness.setUp
    request=Harness.request

    def reviewed(self):
        req={'device':'PC_SUNO_BROWSER','intent':{'motor':'rolling bass',
             'mid':'acid','voice':'mantra','structure':'drop and break',
             'psychoacoustics':'orbit','bpm':144}}
        status,body=self.request('POST','/api/preanalysis',payload=req)
        self.assertEqual(status,200)
        self.assertTrue(body['context_preset']['preset_candidate'])
        return {'preset_id':'http-test','analysis_request':req,'expected_version':0,
                'review_sha256':body['preset_review_sha256'],'creator_approved':True}

    def test_http_save_readback(self):
        payload=self.reviewed()
        status,data=self.request('POST','/api/preset/save',payload=payload)
        self.assertEqual(status,200)
        self.assertEqual(data['saved']['version'],1)
        self.assertEqual(self.request('POST','/api/preset/read',payload={'preset_id':'http-test'}),
                         (200,{'versions':data['versions']}))

    def test_http_security(self):
        payload=self.reviewed()
        for kwargs in ({'origin':'https://external.example'},{'host':'evil.example'}):
            self.assertEqual(self.request('POST','/api/preset/save',payload=payload,**kwargs)[0],403)
        self.assertEqual(self.request('POST','/api/preset/save',payload=dict(payload,creator_approved=False))[0],400)
        self.assertEqual(self.request('POST','/api/preset/read',payload={'preset_id':'../escape'})[0],400)
        self.assertFalse((portable.DATA/'presets').exists())

    def test_stale_intent_and_version(self):
        payload=self.reviewed()
        changed=dict(payload['analysis_request'])
        changed['intent']=dict(changed['intent'],title='changed after review')
        self.assertEqual(self.request('POST','/api/preset/save',payload=dict(payload,analysis_request=changed))[1]['error'],'STALE_PRESET_REVIEW')
        self.assertEqual(self.request('POST','/api/preset/save',payload=payload)[0],200)
        self.assertEqual(self.request('POST','/api/preset/save',payload=payload)[1]['error'],'PRESET_VERSION_CONFLICT')

    def test_concurrent_same_version(self):
        payload=self.reviewed()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:self.request('POST','/api/preset/save',payload=payload),range(2)))
        self.assertEqual(sorted(x[0] for x in results),[200,400])
        self.assertEqual(len(preset_evidence.read_versions(portable.DATA,'http-test')),1)

    def test_unsupported_atomic_publication(self):
        payload=self.reviewed()
        with patch('os.link',side_effect=OSError('unsupported')):
            code,result=self.request('POST','/api/preset/save',payload=payload)
        self.assertEqual((code,result['error']),(400,'PRESET_ATOMIC_PUBLICATION_UNAVAILABLE'))
        self.assertEqual(preset_evidence.read_versions(portable.DATA,'http-test'),[])

    def test_corrupt_nonobject_is_controlled(self):
        payload=self.reviewed()
        self.assertEqual(self.request('POST','/api/preset/save',payload=payload)[0],200)
        (portable.DATA/'presets/http-test/00000001.json').write_text('[]')
        self.assertEqual(self.request('POST','/api/preset/read',payload={'preset_id':'http-test'})[1]['error'],'PRESET_INTEGRITY')

del Harness
