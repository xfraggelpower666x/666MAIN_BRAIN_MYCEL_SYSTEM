import unittest, json, tempfile, shutil
from pathlib import Path
from engine import creator_learning as c, device_output as d, music_memory as m

ROOT=Path(__file__).resolve().parents[1]/'evidence'
class HistoricalMemoryTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'historical_music_memory.json').read_text())
    def test_original_pairs(self):
        self.assertEqual(len(self.data['records']),5)
        self.assertEqual([r['provenance']['message_index_zero_based'] for r in self.data['records']],[13,19,51,77,121])
        for r in self.data['records']:
            self.assertEqual(m.digest(r),r['sha256'])
            self.assertFalse(r['exact_prompt_render_binding'])
            self.assertFalse(r['audio_verified'])
    def test_reference_selection(self):
        result=c.music_memory_audit(ROOT,{})
        self.assertEqual(result['reference_count'],4)
        self.assertNotIn('historical-chat-121',[r['track_id'] for r in result['prompt_history']])
    def test_creator_provenance(self):
        result=c.music_memory_audit(ROOT,{'renderer':'Suno','model':'UNKNOWN','route':'UNKNOWN'})
        self.assertEqual(len(result['historical_observations']),5)
        self.assertEqual(len(result['historical_context_notes']),1)
        self.assertEqual(result['relations'],[])
        self.assertEqual(result['historical_observations'][2]['related_track_ids'],['historical-chat-13','historical-chat-19'])
    def test_device_consumer(self):
        result=d.translate({'genre':'Dark Psychedelic'},'PC_SUNO_BROWSER',evidence_root=ROOT)['production_quality_audit']
        self.assertEqual(result['reference_count'],4)
        self.assertEqual(result['history_status'],'PARTIAL_REFERENCE')
        self.assertTrue(all(r['native_evidence_id'] for r in result['comparisons']))
        self.assertFalse(result['production_authorized'])
    def test_exclude_current(self):
        result=c.music_memory_audit(ROOT,{},'historical-chat-13')
        self.assertEqual(result['reference_count'],3)
        self.assertTrue(all('historical-chat-13' not in r['related_track_ids'] for r in result['historical_observations']))
    def test_tampered(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.data['records'][-1]['style']='tampered'
            (Path(tmp)/'historical_music_memory.json').write_text(json.dumps(self.data))
            with self.assertRaisesRegex(ValueError,'HISTORICAL_INTEGRITY'):
                c.music_memory_audit(tmp,{})
    def test_read_only(self):
        p=ROOT/'historical_music_memory.json'; before=p.read_bytes()
        c.music_memory_audit(ROOT,{})
        self.assertEqual(p.read_bytes(),before)
