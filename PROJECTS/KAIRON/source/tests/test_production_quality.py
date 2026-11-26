import unittest
from engine import production_quality as q, device_output as d
G='Dark Psychedelic, Dark Psytrance, Twisted Dark Goa'
M='dry kick, rolling 1/16 bass, straight groove'
MASTER='club-ready master, maximum clean loudness, punchy transients, tight mono sub, clear spectral and vocal separation, preserved dynamics, no clipping, no overcompression, no digital artifacts'
class QualityTests(unittest.TestCase):
    def test_repeat(self):
        p={'style':M,'extended':'gradual build'}
        self.assertEqual(q.compare(p,p)['status'],'HOLD')
    def test_dynamic(self):
        self.assertEqual(q.compare({'style':M,'extended':'vacuum cut'},{'style':M,'extended':'gradual build'})['status'],'REVIEW')
    def test_unknown(self): self.assertEqual(q.compare({}, {})['axes']['beat']['status'],'UNKNOWN')
    def test_negated(self): self.assertFalse(q.witnesses({'style':'no dry kick'},('dry kick',)))
    def test_avoid(self): self.assertFalse(q.witnesses({'style':'Avoid: dry kick'},('dry kick',)))
    def test_master(self): self.assertTrue(all(all(x.values()) for x in q.mastering({'style':MASTER,'extended':MASTER}).values()))
    def test_master_missing(self): self.assertFalse(q.mastering({'style':MASTER,'extended':''})['extended']['club'])
    def test_duration(self): self.assertEqual(q.duration(dict(bpm=144,bars=216,meter='4/4',start_silence=2.5,end_silence=2.5))['seconds'],365)
    def test_duration_invalid(self): self.assertEqual(q.duration(dict(bpm=True,bars=216,meter='4/4'))['status'],'REVIEW')
    def test_history_missing(self): self.assertEqual(d.translate({'genre':G},'PC_SUNO_BROWSER')['production_quality_audit']['history_status'],'PARTIAL_REFERENCE')
    def test_history_pair(self):
        i={'genre':G,'motor':M}; o=d.translate(i,'PC_SUNO_BROWSER'); p={k:o['fields'][k]['text'] for k in ('style','extended')}; r=d.translate(i,'PC_SUNO_BROWSER',{'production_context':{'prompt_history':[p,p]}})['production_quality_audit']; self.assertEqual(r['reference_count'],1); self.assertIn('REPEATED_MOTOR',r['reasons'])
    def test_dj(self):
        p=dict(entryBpm=144,exitBpm=144,entryMeter='4/4',exitMeter='4/4',gridRestored=True,exitStable=True); r=d.translate({'genre':G},'PC_SUNO_BROWSER',{'production_context':{'dj_plan':p}}); self.assertEqual(r['motor_intelligence_audit']['declared_dj_plan'],'PASS'); self.assertFalse(r['production_quality_audit']['production_authorized'])
    def test_endguard(self):
        r=d.translate({'genre':G,'lyrics':'[ALL VOCALS END HERE]\nFire'},'PC_SUNO_BROWSER')['production_quality_audit']; self.assertIn('VOCAL_END_REVIEW',r['reasons'])
    def test_preserve(self): self.assertEqual(d.translate({'lyrics':'Fire 🔥'},'PC_SUNO_BROWSER')['fields']['lyrics']['text'],'Fire 🔥')
