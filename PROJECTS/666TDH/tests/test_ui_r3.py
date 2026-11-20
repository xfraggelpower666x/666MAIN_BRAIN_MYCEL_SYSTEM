"""Native Benutzerführung und Renderer: deterministische No-Authority-Gegenproben."""
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from runtime.ui.view_model import build_view_model
from runtime.ui.render_html import render_html


class NativeUiR3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binding=json.loads((ROOT/'runtime/facets/SUBFACET_BINDINGS.json').read_text(encoding='utf-8'))
        cls.children={k:{'name':k,'system_id':v['system_id'],'version':v['version'],
                         'current_path':v['current_path']} for k,v in cls.binding['child_profiles'].items()}
        cls.registry={'system_id':'666TRACKHUB-001','children':cls.children}
        cls.routes={'root':['SYSTEMSTART','STATUS','HELP','WEITER','NEW CHAT','DASHBOARD','VISUAL','HOST RECOVERY','UPDATE'],
                    'child':['SYSTEMSTART','STATUS','HELP','WEITER','NEW CHAT','DASHBOARD','VISUAL'],
                    'daemon':['STATUS','NEXT','MENU','CONTINUE','BACK','HELP','STOP','WEITER','NEW CHAT']}

    @classmethod
    def build(cls, token=None, continuity=None):
        return build_view_model(registry=cls.registry,routes=cls.routes,token=token,
            release='v1.15.0',profile=cls.binding['child_profiles'][token] if token else None,
            continuity=continuity,pointer_state='VERIFIED_TEST_CURRENT',files_verified=281)

    def test_root_views_show_real_content_and_verified_count(self):
        data=self.build()
        self.assertEqual(len(data['sections']),4)
        self.assertEqual(len(data['daemon_menu']),9)
        self.assertEqual(len(data['menu']),14)
        self.assertEqual(data['integrity']['verified_files'],281)
        for section in data['sections']:
            self.assertTrue(section['source'])
            self.assertTrue(section['facts'])
            self.assertTrue(section['summary'])
        self.assertIn('FSE',str(data['sections']))

    def test_all_children_have_scoped_views_and_holds(self):
        for token in self.children:
            with self.subTest(token=token):
                data=self.build(token)
                self.assertEqual(data['scope'],token)
                self.assertEqual(data['daemon_menu'],[])
                self.assertEqual(len(data['sections']),len(self.binding['child_profiles'][token]['ui_sections']))
                self.assertTrue(all(s['source'].startswith('runtime/') for s in data['sections']))
                if token in ('FSE','SHACHIVITI'):
                    self.assertTrue(all(s['status']=='HOLD' for s in data['sections']))
                else:
                    self.assertTrue(all(s['status']=='VERIFIZIERTE_KONFIGURATION' for s in data['sections']))

    def test_daemon_checkpoint_is_advisory_not_run(self):
        d=self.build('LCTS',{'status':'LOCAL_SCOPED_CHECKPOINT_UNVERIFIED_TASK'})['companion']
        self.assertEqual(d['state'],'CHECKPOINT_REVIEW_REQUIRED')
        self.assertEqual(d['routing_authority'],'NONE')
        self.assertEqual(d['write_authority'],'NONE')
        self.assertEqual(d['suggested_command'],'666TDH LCTS STATUS')

    def test_renderer_has_real_tabs_and_copy_only_no_external_requests(self):
        data=self.build()
        data['title']='</script><img src=x onerror=alert(1)>'
        data['sections'][0]['facts']=['<script>alert(2)</script>']
        html=render_html(data)
        self.assertNotIn('</script><img src=x onerror=alert(1)>',html)
        self.assertNotIn('<script>alert(2)</script>',html)
        self.assertIn("selectSection(section,section.id)",html)
        self.assertIn("byId('facts').replaceChildren",html)
        self.assertIn("role=\"tablist\"",html)
        self.assertIn('navigator.clipboard.writeText',html)
        self.assertIn('Manuell kopieren:',html)
        self.assertNotIn('fetch(',html)
        self.assertNotIn('XMLHttpRequest',html)
