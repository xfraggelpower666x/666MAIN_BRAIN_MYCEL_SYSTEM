"""Repo-authority integration tests using an isolated miniature current tree."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tdh import Current, CurrentError

class SubfacetRouterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        src=ROOT/'runtime/facets/SUBFACET_BINDINGS.json'
        profiles=json.loads(src.read_text(encoding='utf-8'))
        self.children={}
        files={
            'runtime/facets/SUBFACET_BINDINGS.json':src.read_text(encoding='utf-8'),
            'runtime/facets/SUBFACET_LIFECIRCLE_CONTRACT.md':(ROOT/'runtime/facets/SUBFACET_LIFECIRCLE_CONTRACT.md').read_text(encoding='utf-8'),
            'runtime/ui/INTELLIGENT_UI_CONTRACT.md':(ROOT/'runtime/ui/INTELLIGENT_UI_CONTRACT.md').read_text(encoding='utf-8'),
            'runtime/hub/daemon/DAEMON_COMPANION_CONTRACT.md':(ROOT/'runtime/hub/daemon/DAEMON_COMPANION_CONTRACT.md').read_text(encoding='utf-8'),
            'runtime/LIVECIRCLE.md':'Current root livecircle',
            'runtime/REPO_UPDATE_AUTHORITY.md':('PFS_RUNTIME_AUTHORITY=NONE\nPFS_MUTATION_FROM_TDH=FORBIDDEN\nCURRENT_POINTER_LAST=TRUE\nFSE source-original archive: SOURCE_VAULT_ONLY\n'),
        }
        for token,p in profiles['child_profiles'].items():
            content_state=f'runtime/provider-state/{token}/LIVE_STATE.md'
            identity=f'runtime/children/{token}/SYSTEM_IDENTITY.md'
            bp=[content_state,identity]
            files.update({content_state:'CURRENT',identity:f'SYSTEM_ID={p["system_id"]}',p['visual_adapter_path']:f'Native adapter for {token}'})
            cp={'branch_token':token,'system_id':p['system_id'],'version':p['version'],'parent_system_id':'666TRACKHUB-001','bootstrap':bp}
            files[p['current_path']]=json.dumps(cp)
            self.children[token]={'system_id':p['system_id'],'name':token,'version':p['version'],'current_path':p['current_path'],'bootstrap':[p['current_path'],*bp]}
        registry={'system_id':'666TRACKHUB-001','children':self.children,'visual_bootstrap':['runtime/ui/INTELLIGENT_UI_CONTRACT.md']}
        daemon=['STATUS','NEXT','MENU','CONTINUE','BACK','HELP','STOP','WEITER','NEW CHAT']
        routes={'root':['SYSTEMSTART','STATUS','HELP','WEITER','NEW CHAT','DASHBOARD','VISUAL','UPDATE','HOST RECOVERY'],
                'child':['SYSTEMSTART','STATUS','HELP','WEITER','NEW CHAT','DASHBOARD','VISUAL'],
                'daemon':daemon,
                'descriptions':{x:x for x in ('SYSTEMSTART','STATUS','HELP','WEITER','NEW CHAT','DASHBOARD','VISUAL','UPDATE','HOST RECOVERY',*("DAEMON "+v for v in daemon))}}
        handoff={'system_id':'666TRACKHUB-001','source_release':'v1.15.0','runtime_authority':'NONE','target_branch':None,'status':'CURRENT_IDLE_PENDING_EXTERNAL_HOST_GATE_ONLY','open_step':None,'handoff_id':'handoff-1'}
        files['runtime/REGISTRY.json']=json.dumps(registry)
        files['runtime/TRIGGERS.json']=json.dumps(routes)
        files['continuity/CURRENT_HANDOFF.json']=json.dumps(handoff)
        for path,content in files.items():
            target=self.root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content,encoding='utf-8')
        hashes={name:hashlib.sha256((self.root/name).read_bytes()).hexdigest() for name in files}
        pointer={'system_id':'666TRACKHUB-001','namespace':'666TDH','authority':'REPOSITORY_PROJECT','release':'v1.15.0','state':'TEST_CURRENT',
                 'files':hashes,'bootstrap_order':['runtime/LIVECIRCLE.md','runtime/REPO_UPDATE_AUTHORITY.md','runtime/facets/SUBFACET_BINDINGS.json','runtime/facets/SUBFACET_LIFECIRCLE_CONTRACT.md','runtime/ui/INTELLIGENT_UI_CONTRACT.md','runtime/hub/daemon/DAEMON_COMPANION_CONTRACT.md']}
        (self.root/'CURRENT_POINTER.json').write_text(json.dumps(pointer),encoding='utf-8')
        self.current=Current(self.root)

    def test_root_start_no_child_autoload_and_all_menu_branches(self):
        out=self.current.execute('666TDH SYSTEMSTART',True)
        self.assertIsNone(out['selected_branch'])
        self.assertEqual(len(out['intelligent_ui']['menu']),14)
        self.assertFalse(any(x.startswith('runtime/children/') for x in out['bootstrap']))
        self.assertEqual(out['daemon']['routing_authority'],'NONE')

    def test_five_child_start_bootstrap_is_scoped(self):
        for token in self.children:
            with self.subTest(token=token):
                out=self.current.execute('666TDH '+token+' SYSTEMSTART',True)
                self.assertEqual(out['selected_branch'],token)
                self.assertEqual(out['subfacet']['branch_token'],token)
                self.assertIn(f'runtime/hub/visual_adapters/{token}_VISUAL_ADAPTER.md',out['bootstrap'])
                self.assertFalse(any(p.startswith('runtime/children/') and not p.startswith('runtime/children/'+token+'/') for p in out['bootstrap']))
                self.assertEqual(out['intelligent_ui']['scope'],token)

    def test_child_dashboard_contains_actual_visual_adapter(self):
        out=self.current.execute('666TDH DTSTE DASHBOARD')
        self.assertIn('runtime/hub/visual_adapters/DTSTE_VISUAL_ADAPTER.md',out['bootstrap_order'])
        self.assertEqual(out['visual_host_acceptance'],'OPEN_NOT_VERIFIED')

    def test_scoped_checkpoint_and_negative_branch(self):
        t=self.current.execute('666TDH LCTS NEW CHAT')['checkpoint_template']
        t['open_step']='Section 4'
        ok=self.current.execute('666TDH LCTS WEITER',checkpoint=t)
        self.assertEqual(ok['continuity']['open_step'],'Section 4')
        with self.assertRaisesRegex(CurrentError,'CONFLICT_QUARANTINE'):
            self.current.execute('666TDH TD WEITER',checkpoint=t)
        self.assertEqual(self.current.execute('666TDH TD WEITER')['continuity']['status'],'NO_BOUND_HANDOFF')

    def test_subcircle_position_never_crosses_branch(self):
        t=self.current.execute('666TDH LCTS NEW CHAT')['checkpoint_template']
        t['development_position']='EXTEND'
        self.assertEqual(self.current.execute('666TDH LCTS WEITER',checkpoint=t)['continuity']['development_position'],'EXTEND')
        t['development_position']='EXPORT_REVIEW'
        with self.assertRaisesRegex(CurrentError,'HOLD'):
            self.current.execute('666TDH LCTS WEITER',checkpoint=t)

    def test_daemon_is_advisory_and_no_new_update_router(self):
        for token in self.children:
            result=self.current.execute('666TDH '+token+' STATUS')
            self.assertEqual(result['daemon']['write_authority'],'NONE')
            self.assertEqual(result['daemon']['routing_authority'],'NONE')
            with self.assertRaises(CurrentError):self.current.execute('666TDH '+token+' UPDATE')
        self.assertEqual(self.current.execute('666TDH UPDATE')['publication']['status'],'PREFLIGHT_VERIFIED')
        self.assertEqual(self.current.execute('666TDH DAEMON STATUS')['daemon_operation']['status'],'READ_ONLY_RESPONSE')


    def test_daemon_all_documented_commands_are_root_scoped_read_only(self):
        for cmd in ('STATUS','NEXT','MENU','CONTINUE','BACK','HELP','STOP','WEITER','NEW CHAT'):
            with self.subTest(cmd=cmd):
                got=self.current.execute('666TDH DAEMON '+cmd)
                self.assertIsNone(got['selected_branch'])
                self.assertEqual(got['daemon_operation']['authority'],'NONE')
                self.assertEqual(got['daemon_operation']['persistence'],'NONE')
                self.assertEqual(got['daemon']['routing_authority'],'NONE')
                self.assertEqual(got['daemon']['write_authority'],'NONE')
                if cmd == 'STOP':
                    self.assertEqual(got['daemon_operation']['status'],'SESSION_ONLY_DISPLAY_MUTED')
                if cmd == 'NEW CHAT':
                    self.assertEqual(got['next_chat_trigger'],'666TDH SYSTEMSTART')
        with self.assertRaises(CurrentError):
            self.current.execute('666TDH TD DAEMON STOP')
        with self.assertRaises(CurrentError):
            self.current.execute('666TDH DAEMON UPDATE')

    def test_duplicate_pointer_keys_fail_closed(self):
        p = self.root/'CURRENT_POINTER.json'
        raw=p.read_text(encoding='utf-8')
        p.write_text(raw[:-1]+', "system_id": "666TRACKHUB-001"}',encoding='utf-8')
        with self.assertRaisesRegex(CurrentError,'Doppelter JSON-Schlüssel'):
            Current(self.root)

    def test_tamper_blocks_root_rehydration(self):
        file=self.root/'runtime/facets/SUBFACET_BINDINGS.json'
        file.write_text('{}',encoding='utf-8')
        with self.assertRaisesRegex(CurrentError,'SHA-256'):
            Current(self.root)

if __name__=='__main__':unittest.main()
