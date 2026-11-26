"""Regression for optional Windows gating and native identity preservation."""
import json
import tempfile
import unittest
from pathlib import Path
from guidance import guidance

class NativePriorityR205Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('whole/daemon', 'whole/visual'):
            (self.root/name).mkdir(parents=True)
        (self.root/'whole/visual/MENU.json').write_text(json.dumps({'menu':[{'id':'development'}]}))
        contract={'system_id':'666TDI-001','required_state':['workspace','lineage','facet','last_verified_step','open_gates','next_action'], 'adapters':{'development':{}},'optional_windows_gates':['WINDOWS_BUILD','WINDOWS_PARITY','WINDOWS_HOST_ACCEPTANCE','WINDOWS_REGRESSION','WINDOWS_PACKAGING','WINDOWS_EXE','WINDOWS_CONSUMER_INTEGRATION']}
        (self.root/'whole/daemon/CONTRACT.json').write_text(json.dumps(contract))
        self.state={'system_id':'666TDI-001','workspace':'candidate','lineage':'R20.5','facet':'development','last_verified_step':{'evidence_ref':'commit:verified'},'open_gates':[],'next_action':'continue-native'}
    def check(self,gates):
        return guidance(dict(self.state,open_gates=gates),self.root)
    def test_windows_build_not_blocking(self):
        r=self.check(['WINDOWS_BUILD']);self.assertEqual(r['status'],'GUIDANCE_READY');self.assertEqual(r['next_action'],'continue-native');self.assertEqual(r['optional_windows_gates'],['WINDOWS_BUILD'])
    def test_windows_parity_not_discarded(self):
        r=self.check(['WINDOWS_PARITY','WINDOWS_HOST_ACCEPTANCE']);self.assertEqual(len(r['open_gates']),2);self.assertEqual(r['blocking_gates'],[])
    def test_native_regression_still_blocks(self):
        r=self.check(['WINDOWS_BUILD','NATIVE_REGRESSION']);self.assertEqual(r['status'],'PARTIAL');self.assertEqual(r['blocking_gates'],['NATIVE_REGRESSION'])
    def test_host_acceptance_unqualified_still_blocks(self):
        self.assertEqual(self.check(['HOST_ACCEPTANCE'])['status'],'PARTIAL')
    def test_unknown_gate_fail_closed(self):
        self.assertEqual(self.check(['OTHER_WINDOWS_GATE'])['status'],'PARTIAL')
    def test_foreign_identity_rejected(self):
        with self.assertRaisesRegex(ValueError,'FOREIGN_IDENTITY'):guidance(dict(self.state,system_id='LYVRA'),self.root)
    def test_missing_evidence_still_blocks(self):
        r=guidance(dict(self.state,last_verified_step={}),self.root);self.assertEqual(r['status'],'PARTIAL')
    def test_empty_gates_ready(self):
        self.assertEqual(self.check([])['status'],'GUIDANCE_READY')
    def test_invalid_gate_list_fail_closed(self):
        r=guidance(dict(self.state,open_gates=None),self.root);self.assertEqual(r['status'],'PARTIAL')
if __name__=='__main__':unittest.main()
