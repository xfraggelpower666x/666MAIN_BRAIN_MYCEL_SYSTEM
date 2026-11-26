"""Native 666TDI projection regression (no audio or host dependencies)."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('tdi_semantic_presentation', ROOT / 'facets/semantic_presentation/adapter.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

FIELDS = {'Title': '🧭 Compass', 'Extended': 'Mono low / evolving high', 'Style': 'Dark psy', 'Lyrics': '[HARD STOP]'}
LIMITS = {'Title': 80, 'Extended': 1000, 'Style': 1000, 'Lyrics': 5000}
DECISIONS = [{'cause': 'Compass motif', 'musical_consequence': 'Motif returns changed', 'evidence_ref': 'tdi-track-1'}]

def build(**overrides):
    args = {'track_id': 'track-1', 'mode': 'DISCOVERY', 'decisions': DECISIONS, 'fields': FIELDS, 'limits': LIMITS}
    args.update(overrides)
    return module.assemble(**args)

class PresentationTests(unittest.TestCase):
    def test_utf16_emoji(self): self.assertEqual(module.utf16_units('🧭'), 2)
    def test_output_scope(self):
        out = build()
        self.assertEqual(out['system_id'], '666TDI-001')
        self.assertFalse(out['audio_validated'])
        self.assertFalse(out['host_validated'])
        self.assertEqual(out['copy_fields'][0]['utf16_units'], 10)
    def test_no_source_mutation(self):
        before = dict(FIELDS)
        build()
        self.assertEqual(FIELDS, before)
    def test_reject_overflow(self):
        with self.assertRaisesRegex(module.PresentationError, 'UTF16_LIMIT_EXCEEDED'):
            build(fields={**FIELDS, 'Title': '🧭' * 41})
    def test_requires_explicit_decision_provenance(self):
        with self.assertRaisesRegex(module.PresentationError, 'DECISION_PROVENANCE_MISSING'):
            build(decisions=[{'cause': 'a', 'musical_consequence': 'b'}])
    def test_visual_must_bind_to_real_decision(self):
        with self.assertRaisesRegex(module.PresentationError, 'VISUAL_NOT_DECISION_BOUND'):
            build(visual={'decision_evidence_ref': 'invented'})
    def test_optional_visual(self): self.assertIsNone(build()['visual'])
    def test_no_invented_device_controls(self):
        with self.assertRaisesRegex(module.PresentationError, 'DEVICE_ROUTE_NOT_CONFIRMED'):
            build(device_route={'device': 'PC'})
    def test_copy_and_counters_same_string(self):
        out = build()
        for item in out['copy_fields']:
            self.assertEqual(item['utf16_units'], module.utf16_units(item['payload']))
    def test_mytaste_only_if_present(self):
        out = build(fields={**FIELDS, 'My Taste': 'Human calibrated'}, limits={**LIMITS, 'My Taste': 2000})
        self.assertEqual(out['copy_order'], ['Title', 'Extended', 'My Taste', 'Style', 'Lyrics'])
    def test_no_global_bpm_requirement(self):
        self.assertTrue(build()['source_decisions_only'])
    def test_source_mode_supported(self): self.assertEqual(build(mode='SOURCE')['mode'], 'SOURCE')

if __name__ == '__main__': unittest.main()

