"""R19.9 regression: historical flags and actual text-derived relations."""
import copy
import unittest
from engine import musical_forces as m, semantic_intelligence as s, creative_causal as c, track_preanalysis as p

# Original fixture flags and expected statuses from blob 8cfcf32b7ec41c65785521d08e8c6faca62c1664.
REFERENCE = (
 ('wild_with_direction', {'wild':True,'direction':True}, 'CANDIDATE'),
 ('wild_without_direction', {'wild':True}, 'REVIEW'),
 ('oddity_in_genre', {'oddity':True,'currentCause':True}, 'CANDIDATE'),
 ('unrequested_genre_drift', {'oddity':True,'genreDrift':True}, 'HOLD'),
 ('artistic_dissonance', {'dissonance':True}, 'CANDIDATE'),
 ('technical_damage', {'wild':True,'direction':True,'damage':True}, 'HOLD'),
 ('upper_motion_low_stable', {'perceptual':True,'lowStable':True}, 'CANDIDATE'),
 ('low_anchor_damage', {'perceptual':True,'lowDamage':True}, 'HOLD'),
 ('unverified_rear_claim', {'perceptual':True,'unverifiedClaim':True}, 'HOLD'),
 ('prior_manifesto_leak', {'themeLeak':True}, 'HOLD'),
 ('mastering_or_root_loss', {'guardFail':True}, 'HOLD'),
 ('no_mandatory_chaos', {}, 'REVIEW'),
 ('arbitrary_oddity', {'oddity':True}, 'REVIEW'),
 ('combined_forces', {'wild':True,'direction':True,'oddity':True,'currentCause':True,'perceptual':True,'lowStable':True}, 'CANDIDATE'),
)

class ReferenceTests(unittest.TestCase):
    pass

for name, flags, expected in REFERENCE:
    def test(self, flags=flags, expected=expected):
        self.assertEqual(m.reference_review(flags),expected)
    setattr(ReferenceTests,'test_'+name,test)

class ContextTests(unittest.TestCase):
    def ids(self,r): return {x['id'] for x in r['possibilities']}
    def test_directed(self):
        r=m.assess({'mid':'wild accents','motor':'rolling groove'})
        self.assertEqual(r['status'],'CANDIDATE'); self.assertIn('DIRECTED_CHAOS',self.ids(r))
    def test_wild_alone(self):
        r=m.assess({'mid':'wild accents'}); self.assertEqual(r['status'],'REVIEW'); self.assertFalse(r['possibilities'])
    def test_spectral_causal(self):
        r=m.assess({'motor':'mono sub','high':'stereo orbit'})
        q=r['possibilities'][0]; self.assertEqual(q['id'],'SPECTRAL_MOTION'); self.assertEqual(q['causal_relation']['id'],'STABLE_CORE_MOVING_FIELD')
    def test_negation(self):
        r=m.assess({'motor':'mono sub','high':'no stereo orbit','mid':'no wild accents'})
        self.assertFalse(r['possibilities']); self.assertEqual(r['status'],'REVIEW')
    def test_constraint(self):
        r=m.assess({'motor':'mono sub','high':'stereo orbit','avoid':'mono sub'})
        self.assertNotIn('SPECTRAL_MOTION',self.ids(r))
    def test_no_title_as_motor(self):
        r=m.assess({'title':'mono sub','lyrics':'mono sub','high':'stereo orbit'})
        self.assertNotIn('SPECTRAL_MOTION',self.ids(r))
    def test_emotion_relation(self):
        r=m.assess({'story':'grief becomes hope','structure':'build tension then release'})
        q=next(x for x in r['possibilities'] if x['id']=='EMOTIONAL_RESONANCE'); self.assertEqual(q['causal_relation']['id'],'EXPECTATION_PAYOFF')
    def test_emotion_alone(self):
        r=m.assess({'story':'grief'}); self.assertNotIn('EMOTIONAL_RESONANCE',self.ids(r))
    def test_dialogue(self):
        r=m.assess({'mid':'guitar answers acid'}); self.assertIn('INSTRUMENTAL_CONVERSATION',self.ids(r)); self.assertEqual(r['status'],'CANDIDATE')
        e=r['evidence']['dialogue'][0]; self.assertEqual('guitar answers acid'[slice(*e['span'])],e['text'])
    def test_no_dialogue_from_lyrics(self):
        self.assertFalse(m.assess({'lyrics':'answers acid'})['possibilities'])
    def test_damage_hold(self):
        r=m.assess({'motor':'mono sub','high':'stereo orbit','mid':'digital clipping'})
        self.assertEqual(r['status'],'HOLD'); self.assertTrue(all(q['status']=='HOLD' for q in r['possibilities']))
    def test_negated_damage(self):
        r=m.assess({'motor':'mono sub','high':'stereo orbit','mid':'no digital clipping'})
        self.assertEqual(r['status'],'CANDIDATE')
    def test_unverified_claim(self):
        self.assertEqual(m.assess({'high':'guaranteed rear localization'})['status'],'HOLD')
    def test_preanalysis_integration(self):
        t={'motor':'mono sub','high':'stereo orbit','bpm':144}; before=copy.deepcopy(t)
        r=p.assess(t,s.assess(t),c.assess(t),240)
        self.assertIn('SPECTRAL_MOTION',self.ids(r['musical_forces'])); self.assertEqual(sum(x['bars'] for x in r['chapters']),240); self.assertEqual(t,before)
        self.assertFalse(r['musical_forces']['audio_verified']); self.assertFalse(r['musical_forces']['automatic_promotion'])
    def test_no_preset(self):
        r=m.assess({'genre':'Dark Psytrance'}); self.assertFalse(r['possibilities']); self.assertFalse(r['mandatory_sequence'])
    def test_foreign(self):
        with self.assertRaisesRegex(ValueError,'FOREIGN'): m.assess({'system_id':'LYVRA'})
    def test_no_cross_track(self):
        m.assess({'story':'grief','structure':'build tension then release'}); self.assertFalse(m.assess({})['possibilities'])

if __name__=='__main__': unittest.main()
