import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cls_facet_runtime import facet_model, subfacet_rehydrate

class FacetRuntimeTests(unittest.TestCase):
    def test_main_and_five_subfacets(self):
        result=facet_model(ROOT)
        self.assertEqual(result['system'],'666CLS-CORE-001')
        self.assertEqual(len(result['facets']),5)
        self.assertFalse(result['guide']['auto_run'])
    def test_no_foreign_exec_or_permissions(self):
        result=facet_model(ROOT)
        self.assertTrue(all(not f['actions'] for f in result['facets']))
        self.assertEqual(result['mode'],'READ_ONLY')
        self.assertEqual(result['guide']['write_authority'],False)
    def test_cures_not_reparented(self):
        data=json.loads((ROOT/'facets/FACET_REGISTRY.json').read_text())
        cures=next(x for x in data['sources'] if x['id']=='cures')
        self.assertEqual(cures['system_id'],'666PFS-CURES-001')
        self.assertEqual(cures['classification'],'PFS_CHILD_REFERENCE')
    def test_sources_are_not_promoted(self):
        data=json.loads((ROOT/'facets/FACET_REGISTRY.json').read_text())
        self.assertTrue(all(x['source_status']=='LOCAL_ARCHIVE_VERIFIED_NOT_REMOTE_CURRENT' for x in data['sources']))

    def test_subfacet_rehydration_protects_authority(self):
        result=subfacet_rehydrate(ROOT, 'cures')
        self.assertEqual(result['facet']['native_system_id'],'666PFS-CURES-001')
        self.assertFalse(result['auto_resume'])
        self.assertFalse(result['external_authority_verified'])
    def test_unknown_subfacet_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unregistered subfacet'):
            subfacet_rehydrate(ROOT, 'unknown')
