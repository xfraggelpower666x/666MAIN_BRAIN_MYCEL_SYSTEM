import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from engine import portable as p, relational as r, pattern_relations as q

class PatternRelationTests(unittest.TestCase):
    def setUp(self):
        self.d=tempfile.TemporaryDirectory();self.addCleanup(self.d.cleanup)
        self.path=Path(self.d.name);(self.path/'tracks').mkdir()
        patcher=patch.object(p,'DATA',self.path);patcher.start();self.addCleanup(patcher.stop)
        p.atomic(self.path/'tracks'/'test-track.json',{
          'track_id':'test-track','title':'Pressure Orbit','genre':'dark psytrance',
          'story':'return with history','motor':'straight rolling 16th psybass 4/4',
          'mid':'acid layer mutation','high':'spectral orbit','voice':'whisper spoken',
          'energy':'build tension and contrast for drop','ending':'final hard stop',
          'lyrics':'mantra return with history','avoid':'swing, pop, no static loops'})
        r.build('test-track')
    def test_all_patterns_retained(self):
        x=q.assess('test-track');self.assertEqual(len(x['results']),10)
    def test_causal_witnesses_not_just_hit_count(self):
        x=q.assess('test-track');y=next(i for i in x['results'] if i['candidate_id']=='psy_hypnotic_loop')
        self.assertTrue(any(x['witnesses'] for x in y['matches']))
        self.assertTrue(any(k['risk']=='static_repetition' for k in y['counterrelations']))
    def test_foreign_identity_blocked(self):
        self.assertEqual(q.assess('test-track')['identity'],'666TDI')
        self.assertFalse(q.assess('test-track')['global_promotion'])
    def test_no_auto_graph_mutation(self):
        before=r.read('test-track');q.assess('test-track');self.assertEqual(before,r.read('test-track'))
    def test_no_silent_adoption(self):
        self.assertTrue(all(not x['adopted'] for x in q.assess('test-track')['results']))
    def test_unknown_mappings_not_silent(self):
        x=q.assess('test-track',include_presets=True)
        y=next(i for i in x['results'] if i['candidate_id']=='peak_dirty_clean')
        self.assertTrue(any(i['reason']=='NO_SEMANTIC_MAPPING' for i in y['unresolved']))
    def test_attach_requires_review(self):
        with self.assertRaises(q.PatternRelationError):q.attach_reviewed('test-track','psy_hypnotic_loop','','author',['forward_motion'])
    def test_attach_cannot_invent_support(self):
        with self.assertRaises(q.PatternRelationError):q.attach_reviewed('test-track','psy_hypnotic_loop','reason','author',['human_intimacy'])
    def test_attach_scoped_and_verified_graph(self):
        x=q.attach_reviewed('test-track','psy_hypnotic_loop','Psy motor supports recurrence','creator',['forward_motion'])
        self.assertFalse(x['global_rule']);self.assertFalse(x['audio_verified']);self.assertTrue(r.verify(r.read('test-track')))
        self.assertTrue(any(e['evidence'] for e in r.read('test-track')['edges'].values() if e['relation']=='SUPPORTS'))
    def test_missing_track_fails(self):
        with self.assertRaises(r.GraphError):q.assess('nonexistent')
    def test_no_auto_audio_claim(self):
        self.assertTrue(all(not x['audio_verified'] for x in q.assess('test-track')['results']))
    def test_repeat_assessment_deterministic(self):
        self.assertEqual(q.assess('test-track'),q.assess('test-track'))

if __name__=='__main__':unittest.main()
