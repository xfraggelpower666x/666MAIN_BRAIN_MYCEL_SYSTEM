import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from runtime.facets.lifecycle import FacetError, validate_bindings, scoped_continuity, checkpoint_template, profile_state
from runtime.ui.view_model import build_view_model
from runtime.ui.render_html import render_html


class SubfacetContractTests(unittest.TestCase):
    def setUp(self):
        self.binding=json.loads((ROOT/'runtime/facets/SUBFACET_BINDINGS.json').read_text(encoding='utf-8'))
        self.registry={'system_id':'666TRACKHUB-001','children':{t:{'system_id':p['system_id'],'version':p['version'],'name':t,'current_path':p['current_path']} for t,p in self.binding['child_profiles'].items()}}
        self.routes={'root':['SYSTEMSTART','STATUS','HELP','WEITER','NEW CHAT','DASHBOARD','VISUAL'],'child':['SYSTEMSTART','STATUS','HELP','WEITER','NEW CHAT','DASHBOARD','VISUAL']}
        self.handoff={'target_branch':None,'status':'CURRENT_IDLE_PENDING_EXTERNAL_HOST_GATE_ONLY','open_step':None,'handoff_id':'hub-1'}

    def test_five_isolated_profile_bindings(self):
        validate_bindings(self.binding,self.registry,'666TRACKHUB-001')
        self.assertEqual(set(self.registry['children']),{'TD','LCTS','DTSTE','FSE','SHACHIVITI'})
        for token,p in self.binding['child_profiles'].items():
            state=profile_state(token,p)
            self.assertEqual(state['branch_token'],token)
            self.assertEqual(state['mutation_authority'],'666TDH UPDATE')
            self.assertEqual(state['visual_adapter'],f'runtime/hub/visual_adapters/{token}_VISUAL_ADAPTER.md')
            self.assertNotIn('666TDH '+token+' UPDATE',state.values())

    def test_wrong_or_missing_profile_rejected(self):
        import copy
        bad=copy.deepcopy(self.binding);bad['child_profiles']['TD']['system_id']='OTHER'
        with self.assertRaisesRegex(FacetError,'HOLD'):validate_bindings(bad,self.registry,'666TRACKHUB-001')
        bad=copy.deepcopy(self.binding);bad['child_profiles'].pop('LCTS')
        with self.assertRaisesRegex(FacetError,'HOLD'):validate_bindings(bad,self.registry,'666TRACKHUB-001')

    def test_checkpoint_scope_and_read_only(self):
        payload=checkpoint_template(pointer_raw=b'pointer',release='v1.15.0',target_system_id='666LCTS-001',branch_token='LCTS')
        payload['open_step']='Next validated section'
        got=scoped_continuity(payload,pointer_sha256=payload['pointer_sha256'],release='v1.15.0',target_system_id='666LCTS-001',branch_token='LCTS',provider_handoff=self.handoff)
        self.assertEqual(got['open_step'],'Next validated section')
        self.assertEqual(got['runtime_authority'],'NONE')
        with self.assertRaisesRegex(FacetError,'CONFLICT_QUARANTINE'):
            scoped_continuity(payload,pointer_sha256=payload['pointer_sha256'],release='v1.15.0',target_system_id='666TRACKDESIGN-001',branch_token='TD',provider_handoff=self.handoff)
        self.assertEqual(scoped_continuity(None,pointer_sha256='',release='v1.15.0',target_system_id='',branch_token='FSE',provider_handoff=self.handoff)['status'],'NO_BOUND_HANDOFF')

    def test_menu_only_routed_commands(self):
        ui=build_view_model(registry=self.registry,routes=self.routes,token=None,release='v1.15.0',profile=None,continuity=None,pointer_state='LIVE')
        starts={x['command'] for x in ui['menu'] if x['id'] in self.registry['children']}
        self.assertEqual(starts,{f'666TDH {branch} SYSTEMSTART' for branch in self.registry['children']})
        self.assertFalse(any('666TDH DAEMON' in x['command'] for x in ui['menu']))
        for token,p in self.binding['child_profiles'].items():
            ui=build_view_model(registry=self.registry,routes=self.routes,token=token,release='v1.15.0',profile=p,continuity={'status':'NO_BOUND_HANDOFF'},pointer_state='LIVE')
            self.assertEqual(len(ui['sections']),len(p['ui_sections']))
            self.assertTrue(all(x['command'].startswith('666TDH '+token+' ') or x['id']=='back' for x in ui['menu']))
            self.assertEqual(ui['companion']['routing_authority'],'NONE')
            self.assertEqual(ui['companion']['write_authority'],'NONE')
        self.assertIn('UNRESOLVED_SOURCE_IDENTITY',build_view_model(registry=self.registry,routes=self.routes,token='FSE',profile=self.binding['child_profiles']['FSE'],release='v1.15.0',continuity=None,pointer_state='LIVE')['companion']['holds'])

    def test_offline_ui_copy_only_and_script_escape(self):
        ui=build_view_model(registry=self.registry,routes=self.routes,token=None,release='v1.15.0',profile=None,continuity=None,pointer_state='LIVE')
        ui['title']='</script><script>alert(1)</script>'
        html=render_html(ui)
        self.assertNotIn('</script><script>alert(1)',html)
        self.assertIn('navigator.clipboard.writeText',html)
        self.assertIn('textContent',html)
        self.assertIn('Host-Abnahme',html)
        self.assertNotIn('fetch(',html)


if __name__=='__main__':unittest.main()
