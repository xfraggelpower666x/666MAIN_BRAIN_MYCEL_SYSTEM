import unittest
import tempfile
from pathlib import Path
from engine import creator_learning as c, device_output as d

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=self.tmp.name
        self.intent={'genre':'Dark Psychedelic, Dark Psytrance, Twisted Dark Goa','motor':'dry kick, rolling 1/16 bass, straight groove'}
        out=d.translate(self.intent,'PC_SUNO_BROWSER')
        self.pair={k:out['fields'][k]['text'] for k in ('style','extended')}
        self.context={'model':'synthetic-fixture','route':'PC_BROWSER'}
    def record(self,track='a',rating='SUCCESS',state='ISSUED',**extra):
        return c.record(self.root,dict(track_id=track,decision_id='motor',category='MOTOR',rating=rating,intent_summary='fixture',observed_outcome='fixture',creator_confirmed=True,prompt_pair=self.pair,prompt_state=state,music_context=self.context,**extra))
    def audit(self,**kwargs):
        return d.translate(self.intent,'PC_SUNO_BROWSER',{'production_context':{'music_context':self.context,**kwargs}},evidence_root=self.root)['production_quality_audit']
    def test_native_history(self):
        receipt=self.record(); result=self.audit(); self.assertEqual(result['reference_count'],1); self.assertIn('REPEATED_MOTOR',result['reasons']); self.assertEqual(result['comparisons'][0]['native_evidence_id'],receipt['id'])
    def test_conflict(self):
        self.record(); self.record('b','UNSUCCESSFUL'); self.assertIn('CREATOR_EVIDENCE_CONTRADICTION',self.audit()['reasons'])
    def test_exclude_current(self):
        self.record(); self.assertEqual(self.audit(current_track='a')['reference_count'],0)
    def test_candidate(self):
        self.record(state='CORRECTION_CANDIDATE'); self.assertEqual(self.audit()['reference_count'],0)
    def test_context(self):
        self.record(); self.assertEqual(self.audit(music_context={'model':'other'})['music_memory']['relations'],[])
    def test_none(self):
        self.assertIn('production_quality_audit',d.translate(self.intent,'PC_SUNO_BROWSER',{'production_context':None}))
    def test_invalid_context(self):
        with self.assertRaisesRegex(ValueError,'INVALID_PRODUCTION_CONTEXT'): d.translate(self.intent,'PC_SUNO_BROWSER',{'production_context':[]})
    def test_tamper(self):
        self.record(); p=Path(self.root)/'creator_evidence/a.jsonl'; p.write_text(p.read_text().replace('fixture','altered'))
        with self.assertRaisesRegex(ValueError,'EVIDENCE_HASH_MISMATCH'): self.audit()
    def test_read_only(self):
        self.record(); p=Path(self.root)/'creator_evidence/a.jsonl'; before=p.read_bytes(); self.audit(); self.assertEqual(p.read_bytes(),before)
    def test_legacy(self):
        c.record(self.root,dict(track_id='legacy',decision_id='motor',category='MOTOR',rating='MIXED',intent_summary='fixture',observed_outcome='fixture',creator_confirmed=True)); self.assertEqual(self.audit()['reference_count'],0); self.assertEqual(c.assess(self.root,'legacy')['observations'],1)
