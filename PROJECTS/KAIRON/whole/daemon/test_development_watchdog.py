import unittest
from development_watchdog import evaluate


def h(*phases, task='R20.6'):
    return [{'task':task,'phase':p,'system_id':'666TDI-001'} for p in phases]


class WatchdogTests(unittest.TestCase):
    def test_three_repeated_audits_detected(self):
        x=evaluate(h('AUDIT','PLAN','AUDIT'),current_task='R20.6')
        self.assertEqual(x['status'],'OVERSTEER_DETECTED')
        self.assertEqual(x['recommended_next'],'IMPLEMENT_OR_REPORT_BLOCKER_WITH_EVIDENCE')
    def test_two_does_not_trigger(self):
        self.assertFalse(evaluate(h('AUDIT','PLAN'))['suspected_host_oversteer'])
    def test_different_tasks_not_confused(self):
        entries=h('AUDIT','PLAN',task='OTHER')+h('AUDIT',task='R20.6')
        self.assertFalse(evaluate(entries,current_task='R20.6')['suspected_host_oversteer'])
    def test_claimed_progress_not_trusted(self):
        entries=h('AUDIT','AUDIT')+[{'task':'R20.6','phase':'IMPLEMENT','receipt_verified':True}]+h('PLAN')
        self.assertTrue(evaluate(entries)['suspected_host_oversteer'])
    def test_real_write_resets_oversteer(self):
        x=evaluate(h('AUDIT','PLAN','AUDIT'),trusted_receipts=[{'kind':'SOURCE_WRITE','ref':'sha:a','verified':True}])
        # Ein Write ohne belegte zeitliche Zuordnung kann eine neue Prüfschleife nicht aufheben.
        self.assertEqual(x['status'],'OVERSTEER_DETECTED')
        self.assertTrue(x['architecture_built'])
    def test_previous_write_then_new_loop(self):
        rows=[{'task':'R20.6','phase':'IMPLEMENT','evidence_ref':'sha:old'}]+h('AUDIT','PLAN','AUDIT')
        proof=[{'kind':'SOURCE_WRITE','ref':'sha:old','task':'R20.6','verified':True}]
        self.assertTrue(evaluate(rows,current_task='R20.6',trusted_receipts=proof)['suspected_host_oversteer'])
    def test_task_bound_write_resets_only_current_segment(self):
        rows=h('AUDIT','PLAN','AUDIT')+[{'task':'R20.6','phase':'IMPLEMENT','evidence_ref':'sha:new'}]+h('AUDIT')
        proof=[{'kind':'SOURCE_WRITE','ref':'sha:new','task':'R20.6','verified':True}]
        view=evaluate(rows,current_task='R20.6',trusted_receipts=proof)
        self.assertEqual(view['repeat_count'],1)
        self.assertFalse(view['suspected_host_oversteer'])
    def test_other_task_receipt_cannot_clear(self):
        proof=[{'kind':'SOURCE_WRITE','ref':'sha:b','task':'OTHER','verified':True}]
        self.assertTrue(evaluate(h('AUDIT','PLAN','AUDIT'),current_task='R20.6',trusted_receipts=proof)['suspected_host_oversteer'])
    def test_unscoped_receipt_cannot_clear_bound_task(self):
        proof=[{'kind':'SOURCE_WRITE','ref':'sha:old','verified':True}]
        self.assertTrue(evaluate(h('AUDIT','PLAN','AUDIT'),current_task='R20.6',trusted_receipts=proof)['suspected_host_oversteer'])
    def test_untrusted_receipt_does_not_reset(self):
        x=evaluate(h('AUDIT','PLAN','AUDIT'),trusted_receipts=[{'kind':'SOURCE_WRITE','ref':'sha:a','verified':False}])
        self.assertTrue(x['suspected_host_oversteer'])
    def test_readback_alone_not_code_build(self):
        x=evaluate(h('AUDIT','PLAN','AUDIT'),trusted_receipts=[{'kind':'DIRECT_READBACK','ref':'sha:a','verified':True}])
        self.assertFalse(x['architecture_built'])
    def test_three_verifications(self):
        x=evaluate(h('IMPLEMENT'),trusted_receipts=[{'kind':kind,'ref':kind,'verified':True} for kind in ('SOURCE_WRITE','REGRESSION_PASS','DIRECT_READBACK')])
        self.assertTrue(x['architecture_built'] and x['regression_verified'] and x['readback_verified'])
        self.assertFalse(x['release_authorized'])
    def test_foreign_context_rejected(self):
        with self.assertRaisesRegex(ValueError,'FOREIGN_CONTEXT'):evaluate([],active_namespace='LYVRA')
    def test_foreign_history_rejected(self):
        with self.assertRaisesRegex(ValueError,'FOREIGN_HISTORY'):evaluate([{'system_id':'LYVRA','task':'x','phase':'AUDIT'}])
    def test_bad_history_rejected(self):
        with self.assertRaisesRegex(ValueError,'INVALID_HISTORY_ENTRY'):evaluate(['AUDIT'])
    def test_threshold_validated(self):
        with self.assertRaisesRegex(ValueError,'INVALID_WATCHDOG_INPUT'):evaluate([],threshold=1)
    def test_history_bound(self):
        with self.assertRaisesRegex(ValueError,'HISTORY_LIMIT_EXCEEDED'):evaluate(h(*(['AUDIT']*257)))
    def test_non_autonomous(self):
        x=evaluate(h('AUDIT','AUDIT','AUDIT'))
        self.assertFalse(x['automatic_dispatch'] or x['mutation'] or x['host_oversteer_prevented'])


if __name__=='__main__':unittest.main()
