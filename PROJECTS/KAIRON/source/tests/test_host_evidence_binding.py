import hashlib
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from engine import daemon_cli as daemon, portable, creator_learning as c

class HostEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'runtime'
        self.patcher=patch.object(portable,'DATA',self.root); self.patcher.start(); self.addCleanup(self.patcher.stop)
        self.payload={'device':'PC_SUNO_BROWSER','intent':{'genre':'Dark Psychedelic','motor':'dry kick, rolling 1/16 bass, straight groove'}}
        self.historical=portable.ROOT/'evidence'/'historical_music_memory.json'
    def quality(self,payload=None):
        return daemon.preanalysis(payload or self.payload)['device_output']['production_quality_audit']
    def test_default_binding(self):
        q=self.quality(); self.assertEqual(q['reference_count'],4); self.assertFalse(q['production_authorized']); self.assertFalse(self.root.exists())
    def test_local_and_historical(self):
        d=daemon.preanalysis(self.payload)['device_output']; pair={k:d['fields'][k]['text'] for k in ('style','extended')}
        before=self.historical.read_bytes()
        receipt=c.record(self.root,dict(track_id='local-a',decision_id='motor',category='MOTOR',rating='SUCCESS',intent_summary='fixture',observed_outcome='fixture',creator_confirmed=True,prompt_pair=pair,prompt_state='ISSUED',music_context={'model':'fixture'}))
        local=self.root/'creator_evidence'/'local-a.jsonl'; snapshot=local.read_bytes()
        q=self.quality(); self.assertEqual(q['reference_count'],5); self.assertIn(receipt['id'],[x['native_evidence_id'] for x in q['comparisons']]); self.assertEqual(local.read_bytes(),snapshot); self.assertEqual(self.historical.read_bytes(),before)
    def test_missing_bundled_source(self):
        with patch.object(portable,'ROOT',Path(self.tmp.name)):
            with self.assertRaisesRegex(ValueError,'HISTORICAL_SOURCE_MISSING'): self.quality()
    def test_client_cannot_choose_root(self):
        self.payload['route_context']={'evidence_root':'/nonexistent','historical_root':'/nonexistent'}
        self.assertEqual(self.quality()['reference_count'],4)
    def test_real_http_preanalysis(self):
        with ThreadingHTTPServer(('127.0.0.1',0),daemon.Handler) as server:
            t=threading.Thread(target=server.serve_forever,daemon=True); t.start()
            try:
                conn=HTTPConnection('127.0.0.1',server.server_port,timeout=5)
                try:
                    conn.request('POST','/api/preanalysis',json.dumps(self.payload),{'Content-Type':'application/json'})
                    response=conn.getresponse(); body=json.loads(response.read()); self.assertEqual(response.status,200); self.assertEqual(body['device_output']['production_quality_audit']['reference_count'],4)
                finally: conn.close()
            finally: server.shutdown(); t.join(5)
