import unittest
from engine import music_memory as m

def seal(**x):
    x['system_id']=m.SYSTEM_ID; x['sha256']=m.digest(x); return x
class MusicMemoryTests(unittest.TestCase):
    def pair(self,track='a',state='ISSUED'):
        return seal(track_id=track,state=state,style='dry kick',extended='vacuum cut')
    def test_dedup(self): self.assertEqual(len(m.history([self.pair(),self.pair('b')])),1)
    def test_current(self): self.assertEqual(m.history([self.pair()], 'a'),[])
    def test_candidate(self): self.assertEqual(m.history([self.pair(state='CORRECTION_CANDIDATE')]),[])
    def test_tamper(self):
        r=self.pair(); r['style']='changed'
        with self.assertRaises(ValueError): m.history([r])
    def test_conflict(self):
        c={'model':'test-fixture','route':'PC_BROWSER'}
        rows=[seal(context=c,creator_confirmed=True,decision_id='motor',rating=x) for x in ('SUCCESS','UNSUCCESSFUL')]
        self.assertEqual(m.relations(rows,c)[0]['status'],'CONTRADICTION_REVIEW')
    def test_context(self):
        r=seal(context={'model':'a'},creator_confirmed=True,decision_id='motor',rating='SUCCESS')
        self.assertEqual(m.relations([r],{'model':'b'}),[])
    def test_unknown(self): self.assertEqual(m.relations([],{'model':'UNKNOWN'}),[])
