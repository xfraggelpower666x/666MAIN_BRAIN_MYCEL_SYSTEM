"""Targeted R1.5 regression; no provider or audio claims."""
import unittest
from engine import semantic_reinforcement as sr, device_output

class ReinforcementTests(unittest.TestCase):
    def test_negated_anchor(self):
        self.assertFalse(sr.assess({"lyrics":"No fire"})["candidates"])
    def test_positive_anchor(self):
        a=sr.assess({"lyrics":"Feel the fire"})
        self.assertEqual(a["candidates"][0]["symbol"],"🔥")
    def test_three_surfaces(self):
        a=sr.assess({"energy":"electric energy","mid":"spiral rotation","lyrics":"fire"})
        self.assertEqual({x["field"] for x in a["candidates"]},{"extended","style","lyrics"})
    def test_exact_words_and_utf16(self):
        b={"start":0,"end":4,"anchor":"Fire","symbol":"🔥🔥🔥","creator_approved":True}
        self.assertEqual(sr.apply_reviewed_bindings("Fire",[b],11),"Fire 🔥🔥🔥")
        with self.assertRaisesRegex(ValueError,"OVER_REFERENCE_BUDGET"):
            sr.apply_reviewed_bindings("Fire",[b],10)
    def test_unapproved(self):
        with self.assertRaisesRegex(ValueError,"APPROVAL"):
            sr.apply_reviewed_bindings("Fire",[{"start":0,"end":4,"anchor":"Fire","symbol":"🔥"}],20)
    def test_stale_span(self):
        with self.assertRaisesRegex(ValueError,"STALE"):
            sr.apply_reviewed_bindings("Fire",[{"start":0,"end":4,"anchor":"Rain","symbol":"🔥","creator_approved":True}],20)
    def test_response_and_terminal(self):
        a=sr.lyric_relations("Fire\n(Fire)\n[ALL VOCALS END HERE 🛑]\n[Instrumental reactivation]\n[Final stop 🛑🔚]")
        self.assertEqual(a["rows"][1]["role"],"RESPONSE_CANDIDATE")
        self.assertTrue(a["vocal_end_present"])
        self.assertFalse(a["review_required"])
    def test_vocal_return(self):
        a=sr.lyric_relations("[ALL VOCALS END HERE]\n[Instrumental]\n(Fire)")
        self.assertEqual(a["post_end_vocal_candidates"],[3])
    def test_bpm_independence(self):
        for bpm in (142,150,152):
            self.assertFalse(sr.assess({"bpm":bpm})["hardness_from_bpm"])
    def test_genre_order(self):
        a=sr.assess({"genre":"Dark Forest Psytrance, Dark Full-On, Goa Trance"})
        self.assertEqual(a["genre_roles"],["Dark Forest Psytrance","Dark Full-On","Goa Trance"])
    def test_output_audit(self):
        x=device_output.translate({"lyrics":"Fire 🔥","mid":"spiral","ending":"final stop"},"IPHONE_SUNO_APP")
        self.assertEqual(x["fields"]["lyrics"]["text"],"Fire 🔥")
        self.assertEqual(x["fields"]["lyrics"]["utf16_units"],7)
        self.assertEqual(x["semantic_reinforcement_audit"]["status"],"CREATOR_REVIEW")

if __name__=="__main__":
    unittest.main()
