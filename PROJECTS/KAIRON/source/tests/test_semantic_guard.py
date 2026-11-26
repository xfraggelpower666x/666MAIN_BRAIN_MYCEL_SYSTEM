import unittest
from engine import semantic_guard as g, device_output as d

class GuardTests(unittest.TestCase):
    def binding(self, anchor='Fire', symbol='🔥', start=0, end=4, approved=True):
        return dict(anchor=anchor,symbol=symbol,start=start,end=end,creator_approved=approved)
    def test_exact_positive(self):
        self.assertEqual(g.reviewed_variant('Fire',[self.binding()],7),'Fire 🔥')
    def test_wrong_symbol(self):
        with self.assertRaisesRegex(ValueError,'SYMBOL_ANCHOR'): g.reviewed_variant('Fire',[self.binding(symbol='🔇')],20)
    def test_negated(self):
        with self.assertRaisesRegex(ValueError,'NONPOSITIVE'): g.reviewed_variant('No Fire',[self.binding(start=3,end=7)],20)
    def test_unapproved(self):
        with self.assertRaisesRegex(ValueError,'APPROVAL'): g.reviewed_variant('Fire',[self.binding(approved=False)],20)
    def test_utf16(self):
        with self.assertRaisesRegex(ValueError,'OVER_REFERENCE'): g.reviewed_variant('Fire',[self.binding(symbol='🔥🔥')],8)
    def test_overlap(self):
        with self.assertRaisesRegex(ValueError,'OVERLAPPING'): g.reviewed_variant('Fire',[self.binding(),self.binding()],20)
    def test_no_silent_rewrite(self):
        x=d.translate({'lyrics':'Fire'},'IPHONE_SUNO_APP'); self.assertEqual(x['fields']['lyrics']['text'],'Fire'); self.assertEqual(x['semantic_reinforcement_audit']['status'],'CREATOR_REVIEW')
    def test_negation_scope(self):
        self.assertEqual(list(g.occurrences('No fire, but fire','fire')),[(13,17)])
    def test_wrong_line_symbol(self):
        x=d.translate({'lyrics':'Fire, fire 🔥'},'PC_SUNO_BROWSER'); self.assertEqual([v['review_required'] for v in x['semantic_reinforcement_audit']['checks']],[True,False])
    def test_vocal_command(self):
        x=d.translate({'lyrics':'[ALL VOCALS END HERE]\n[Choir returns]'},'PC_SUNO_BROWSER'); self.assertEqual(x['semantic_reinforcement_audit']['lyric_relations']['post_end_command_review'],[2])
    def test_instrumental(self):
        x=d.translate({'lyrics':'[ALL VOCALS END HERE]\n[Instrumental reactivation]\n[Final stop 🛑🔚]'},'PC_SUNO_BROWSER'); self.assertFalse(x['semantic_reinforcement_audit']['lyric_relations']['review_required'])
    def test_vacuum_not_silence(self):
        self.assertEqual(list(g.occurrences('vacuum cut','complete silence')),[])
