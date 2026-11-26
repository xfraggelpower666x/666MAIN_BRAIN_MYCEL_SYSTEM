import unittest
from engine import motor_intelligence as m, device_output as d
GOOD='146 BPM, Dark Psychedelic, Dark Full-On Psytrance, Dark Forest Psytrance, tight kick and rolling bass. Restore 146 BPM and stable original beatgrid before DJ outro.'
PLAN=dict(entryBpm=146,exitBpm=146,entryMeter='4/4',exitMeter='4/4',gridRestored=True,exitStable=True)
CASES=[('valid_both',GOOD,GOOD,'PASS'),('metadata_optional','Dark Psychedelic, Dark Psytrance, Twisted Dark Goa, kick',GOOD,'PASS'),('key_metadata','146 BPM, F minor, Dark Psychedelic, Dark Forest Psytrance, Dark Psytechno, kick',GOOD,'PASS'),('front_displaced','146 BPM, Experimental, Dark Psychedelic, Dark Full-On Psytrance, Dark Forest Psytrance',GOOD,'HOLD'),('duplicate','Dark Psychedelic, Dark Forest Psytrance, Dark Forest Psytrance',GOOD,'HOLD'),('negation','Dark Psychedelic, no Dark Full-On Psytrance, Dark Forest Psytrance',GOOD,'HOLD'),('extended_missing',GOOD,'Dark Psychedelic, Dark Forest Psytrance, kick','HOLD')]
DJ=[('stable_entry_exit',PLAN,'PASS'),('intentional_interior_variation',PLAN|dict(interiorVariation=True,explicit=True),'PASS'),('exit_tempo_drift',PLAN|dict(exitBpm=145),'HOLD'),('same_bpm_wrong_grid',PLAN|dict(gridRestored=False),'HOLD'),('unstable_exit',PLAN|dict(exitStable=False),'HOLD'),('meter_not_restored',PLAN|dict(exitMeter='3/4'),'HOLD'),('unintended_interior_tempo_excursion',PLAN|dict(interiorVariation=True,explicit=False),'HOLD'),('missing_exit_evidence',dict(entryBpm=146),'OPEN')]
class ReferenceTests(unittest.TestCase): pass
for name,a,b,e in CASES:
    setattr(ReferenceTests,'test_'+name,lambda self,a=a,b=b,e=e:self.assertEqual(m.reference_review(dict(style=a,extended=b)),e))
for name,p,e in DJ:
    setattr(ReferenceTests,'test_'+name,lambda self,p=p,e=e:self.assertEqual(m.reference_review(p),e))
class MotorTests(unittest.TestCase):
    def output(self,**kw): return d.translate(dict(genre='Dark Psychedelic, Dark Psytrance, Twisted Dark Goa',**kw),'PC_SUNO_BROWSER')
    def test_both_fields(self):
        r=self.output(); self.assertTrue(all(x['status']=='PASS' for x in r['motor_intelligence_audit']['genre_front'].values()))
    def test_preserve_lyrics(self): self.assertEqual(self.output(lyrics='Fire 🔥')['fields']['lyrics']['text'],'Fire 🔥')
    def test_missing_root_hold(self): self.assertEqual(d.translate({'genre':'Dark Psytrance'},'IPHONE_SUNO_APP')['motor_intelligence_audit']['status'],'HOLD')
    def test_bpm_independent(self):
        for bpm in (142,150,153): self.assertFalse(self.output(bpm=bpm)['motor_intelligence_audit']['hardness_from_bpm'])
    def test_layers(self):
        x=self.output(motor='mono sub',mid='rhythmic accents; mutating timbres',high='stereo orbit')['motor_intelligence_audit']; self.assertTrue(all(y['evidence'] for y in x['layers'].values())); self.assertEqual(len(x['relations']),3)
    def test_no_invention(self): self.assertFalse(self.output()['motor_intelligence_audit']['relations'])
    def test_negation(self): self.assertFalse(self.output(motor='mono sub',high='no stereo orbit')['motor_intelligence_audit']['relations'])
    def test_budget(self): self.assertEqual(self.output(story='a'*1001)['motor_intelligence_audit']['status'],'HOLD')
    def test_no_audio_pass(self):
        x=self.output()['motor_intelligence_audit']; self.assertFalse(x['audio_verified']); self.assertFalse(x['production_authorized']); self.assertEqual(x['declared_dj_plan'],'OPEN')
    def test_invalid_boolean(self): self.assertEqual(m.dj_review(PLAN|dict(gridRestored='true')),'HOLD')
    def test_negative_bpm(self): self.assertEqual(m.dj_review(PLAN|dict(entryBpm=-1,exitBpm=-1)),'HOLD')
    def test_emoji_retained(self): self.assertIn('semantic_reinforcement_audit',self.output(lyrics='Fire 🔥'))
