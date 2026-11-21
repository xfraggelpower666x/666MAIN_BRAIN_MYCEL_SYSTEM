import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from engine import portable as p,relational as r

class RelationalTests(unittest.TestCase):
    def setUp(self):
        self.d=tempfile.TemporaryDirectory();self.addCleanup(self.d.cleanup)
        self.path=Path(self.d.name);(self.path/'tracks').mkdir()
        self.patch=patch.object(p,'DATA',self.path);self.patch.start();self.addCleanup(self.patch.stop)
        p.atomic(self.path/'tracks'/'test-track.json',{'track_id':'test-track','story':'awakening','motor':'straight psybass','mid':'acid','high':'spatial motion','voice':'spoken','energy':'pressure','ending':'hard stop','lyrics':'rise'})
    def test_graph_build(self):
        x=r.build('test-track');self.assertGreaterEqual(x['node_count'],7);self.assertGreaterEqual(x['edge_count'],4)
    def test_build_idempotent(self):
        x=r.build('test-track');y=r.build('test-track');self.assertEqual(x['revision'],y['revision'])
    def test_feedback_not_global(self):
        x=r.outcome('test-track','suno','straight bass','swing bass');self.assertFalse(x['global_rule'])
    def test_measurement_requires_artifact(self):
        with self.assertRaises(r.GraphError):r.outcome('test-track','suno','straight bass','swing','MEASURED_AUDIO')
    def test_failure_attribution_requires_review(self):
        x=r.outcome('test-track','suno','motor','swing')
        with self.assertRaises(r.GraphError):r.classify('test-track',x['id'],'TRANSLATION_FAILURE')
        self.assertEqual(r.classify('test-track',x['id'],'UNKNOWN')['status'],'HYPOTHESIS')
    def test_review_does_not_promote(self):
        x=r.outcome('test-track','suno','motor','swing')
        y=r.classify('test-track',x['id'],'TRANSLATION_FAILURE','source-a','creator')
        self.assertFalse(y['global_rule'])
    def test_missing_endpoint_rejected(self):
        a=r.node('test-track','MOTOR','x','reason')
        with self.assertRaises(r.GraphError):r.edge('test-track',a['id'],'bad','CAUSES','reason')
    def test_rehydration_detects_corruption(self):
        r.build('test-track');g=p.load(self.path/'relations'/'test-track.json');g['edges']['bad']={'id':'bad','from':'none','to':'none','relation':'CAUSES'}
        p.atomic(self.path/'relations'/'test-track.json',g)
        self.assertEqual(r.rehydrate()['status'],'PARTIAL')
    def test_no_audio_claim(self):self.assertFalse(r.inspect('test-track')['audio_verified'])
    def test_path_guard(self):
        with self.assertRaises(r.GraphError):r.read('../secret')
    def test_own_identity(self):self.assertEqual(r.blank('t')['system_id'],'666TDI-001')
if __name__=='__main__':unittest.main()
