import unittest
from engine import source_adapters as a

class TestR06(unittest.TestCase):
    def test_inventory(self):self.assertEqual(len(a.intake_registry()),8)
    def test_current_identity(self):self.assertEqual(a.candidate_catalog()['character_pronouns'],'er/ihn/ihm')
    def test_not_automatically_applied(self):
        c=a.candidate_catalog();self.assertTrue(all(x['status'].startswith('HISTORICAL') for k in ('patterns','presets') for x in c[k]))
    def test_match_no_default(self):self.assertEqual(a.match_patterns('unrelated xyz qwerty'),[])
    def test_bad_input(self):
        with self.assertRaises(a.AdapterError):a.match_patterns(None)
    def test_count_emoji(self):
        self.assertEqual(a.character_count('🧠'),1);self.assertEqual(a.character_count('🧠','utf16_units'),2)
    def test_count_crlf(self):self.assertEqual(a.character_count('x\r\ny'),4)
    def test_field_limit(self):self.assertFalse(a.field_audit('abcd',3)['fits'])
    def test_unsupported_mode(self):
        with self.assertRaises(a.AdapterError):a.character_count('x','graphemes')
    def test_ace_no_cloud(self):self.assertFalse(a.ace_step_intake()['actual_audio_render'])
    def test_zero_repo_writes(self):self.assertTrue(all(not x['repo_write_allowed'] for x in a.intake_registry()))
    def test_char_identity_guard(self):
        from unittest.mock import patch
        x=a.candidate_catalog();x['identity']='LYVRA'
        with patch('json.loads',return_value=x):
            with self.assertRaises(a.AdapterError):a.candidate_catalog()
if __name__=='__main__':unittest.main()
