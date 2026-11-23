import unittest,datetime as dt
from engine import heritage as h
class HeritageTests(unittest.TestCase):
 def test_no_forced_bpm(self):self.assertIsNone(h.style_context('bunker spoken psytechno')['bpm'])
 def test_afro_kept(self):self.assertEqual(h.style_context('Nigerian Pidgin afro talking drum')['candidate'],'LINE_C')
 def test_no_default(self):self.assertIsNone(h.style_context('an unrelated story')['candidate'])
 def test_ambiguous(self):self.assertIsNone(h.style_context('bunker and afro')['candidate'])
 def test_explicit_override(self):self.assertEqual(h.style_context('forest',explicit='LINE_C')['candidate'],'LINE_C')
 def test_invalid_style(self):
  with self.assertRaises(ValueError):h.style_context('x','LINE_Z')
 def test_review_non_destructive(self):
  # Reference-only function against empty runtime ledger; no destructive writes.
  out=h.memory_review()
  self.assertTrue(all(not x['automatically_deleted'] for x in out['entries']))
 def test_separation(self):self.assertFalse(h.role_boundary('MUSIC_AUTHORING')['automatic_cross_mode_activation'])
 def test_invalid_mode(self):
  with self.assertRaises(ValueError):h.role_boundary('LIVE_LYVRA')
 def test_male_character(self):self.assertEqual(h.character_identity_guard('historical source')['character_name'],'666TDI')
