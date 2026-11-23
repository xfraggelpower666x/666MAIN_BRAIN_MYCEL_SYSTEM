import sys, unittest, tempfile, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from framework_source_catalog import summary,load_catalog
from archive_console import Console
from cls_livecircle import SYSTEM,write

class SourceCatalogTests(unittest.TestCase):
    def test_unique_sources_and_no_promotion(self):
        items=load_catalog()['sources']; self.assertEqual(len(items),9)
        self.assertTrue(all(row['promotion']=='NOT_AUTHORIZED' and row['foreign_autoload'] is False for row in items))
    def test_native_boundaries(self):
        data=summary(); d={x['id']:x for x in data['sources']}
        self.assertEqual(d['CTGLE']['classification'],'ADDON_CANDIDATE')
        self.assertIn('666PFS',d['666UMIP']['owner_scope'])
        self.assertEqual(d['ONE_FAMILY_IN_THE_SOUND']['classification'],'OUTPUT_ARTIFACT')
    def test_catalog_in_console_does_not_grant_rights(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            write(p/'clients.json',{'system_id':SYSTEM,'clients':{'existing':{'read':['LYRICS'],'submit':[]}}})
            write(p/'frameworks.json',{'frameworks':{'existing':{'name':'Existing','authority':'native','revision':'1','actions':{}}}})
            console=Console(ROOT,p,'reviewer');model=console.model()
            self.assertIn('existing',[x['id'] for x in model['frameworks']]);self.assertEqual(model['source_catalog']['source_count'],9)
            self.assertEqual(model['frameworks'][0]['read'],['LYRICS'])
            self.assertNotIn('CTGLE',console.registry())
            self.assertNotIn('666MIRA',console.registry())
    def test_corrupt_authority_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'bad.json';x=load_catalog();x['sources'][0]['promotion']='LIVE';path.write_text(json.dumps(x),encoding='utf8')
            with self.assertRaisesRegex(ValueError,'authority'):load_catalog(path)
