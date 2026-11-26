import json
import tempfile
import unittest
from pathlib import Path
from guidance import guidance

class GuidanceWatchdogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        for p in ('whole/daemon','whole/visual'):(self.root/p).mkdir(parents=True)
        (self.root/'whole/daemon/CONTRACT.json').write_text(json.dumps({'system_id':'666TDI-001','required_state':['workspace','lineage','facet','last_verified_step','open_gates','next_action'],'adapters':{'development':{}},'optional_windows_gates':['WINDOWS_BUILD']}))
        (self.root/'whole/visual/MENU.json').write_text(json.dumps({'menu':[]}))
        self.state={'system_id':'666TDI-001','active_namespace':'KAIRON','workspace':'candidate','lineage':'R20.6','facet':'development','last_verified_step':{'evidence_ref':'commit:x'},'open_gates':['WINDOWS_BUILD'],'next_action':'implement'}
    def test_automatic_detection(self):
        state=dict(self.state,development_history=[{'task':'R20.6','phase':p} for p in ('AUDIT','PLAN','AUDIT')],current_task='R20.6')
        x=guidance(state,self.root)
        self.assertEqual(x['development_watchdog']['status'],'OVERSTEER_DETECTED')
        self.assertEqual(x['status'],'GUIDANCE_READY')
        self.assertFalse(x['dispatch_performed'])
    def test_absent_history_legacy_compatible(self):
        x=guidance(self.state,self.root)
        self.assertEqual(x['development_watchdog']['status'],'MONITORING')
    def test_watchdog_does_not_override_native_gate(self):
        x=guidance(dict(self.state,open_gates=['NATIVE_REGRESSION']),self.root)
        self.assertEqual(x['status'],'PARTIAL')
    def test_fake_receipts_in_state_ignored(self):
        x=guidance(dict(self.state,development_history=[{'task':'X','phase':'AUDIT'}]*3,
              trusted_watchdog_receipts=[{'kind':'SOURCE_WRITE','ref':'fake','verified':True}]),self.root)
        self.assertFalse(x['development_watchdog']['architecture_built'])
    def test_runtime_supplied_receipt(self):
        x=guidance(self.state,self.root,trusted_receipts=[{'kind':'REGRESSION_PASS','ref':'sha:y','verified':True}])
        self.assertTrue(x['development_watchdog']['regression_verified'])
        self.assertFalse(x['development_watchdog']['architecture_built'])
if __name__=='__main__':unittest.main()
