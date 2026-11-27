import unittest
from update_coordinator import SYSTEM, PLUGIN, REPO, BRANCH, TARGET, CHECKPOINT, inventory
from post_update_host import run_post_update

class FakeHost:
    def __init__(self):
        self.files={'plugin.json':b'{}','.codex-plugin/plugin.json':b'{}','skills/test/SKILL.md':b'original'}
        self.release='old'; self.head='a'*40; self.source={}; self.checkpoint={}; self.calls=[]
        self.fail_checkpoint=False
    def read_native(self,head):
        return dict(system_id=SYSTEM,repository=REPO,branch=BRANCH,head=head,readback_verified=True,regression_passed=True,recovery_verified=True)
    def read_target(self):
        return dict(system_id=SYSTEM,repository=REPO,branch=BRANCH,path=TARGET,checkpoint=CHECKPOINT,authority=False,plugin_id=PLUGIN,cost_limit=0)
    def read_plugin(self,p):
        return dict(plugin_id=p,release_id=self.release,files=dict(self.files))
    def read_backup(self):
        return dict(head=self.head,source_files=dict(self.source),checkpoint=dict(self.checkpoint))
    def additional_cost(self): return 0
    def save_release_recovery(self,p,old): return dict(release_id=old,verified=True)
    def publish_plugin(self,p,files,expected_release_id):
        assert expected_release_id==self.release
        self.calls.append('release'); self.files=dict(files); self.release='new'
    def save_backup_recovery(self,head): return dict(head=head,verified=True)
    def publish_backup_source(self,entries,expected_head):
        assert expected_head==self.head
        self.calls.append('source'); self.source={k[len(TARGET):]:v for k,v in entries.items()}; self.head='b'*40
    def publish_checkpoint(self,path,checkpoint,expected_head):
        assert path==CHECKPOINT and expected_head==self.head
        if self.fail_checkpoint: raise RuntimeError('interrupted')
        self.calls.append('checkpoint'); self.checkpoint=dict(checkpoint); self.head='c'*40

class HostTests(unittest.TestCase):
    def test_full_sequence(self):
        h=FakeHost(); desired=dict(h.files); desired['skills/test/SKILL.md']=b'new'
        r=run_post_update(h,native_head='d'*40,desired_files=desired,execute=True)
        self.assertEqual(h.calls,['release','source','checkpoint'])
        self.assertEqual(r['status'],'BACKUP_VERIFIED')
        self.assertEqual(r['host_acceptance'],'UNATTESTED')
    def test_retry_does_not_republish(self):
        h=FakeHost(); desired=dict(h.files); desired['skills/test/SKILL.md']=b'new'
        h.fail_checkpoint=True
        with self.assertRaises(RuntimeError): run_post_update(h,native_head='d'*40,desired_files=desired,execute=True)
        h.fail_checkpoint=False
        run_post_update(h,native_head='d'*40,desired_files=desired,execute=True)
        self.assertEqual(h.calls,['release','source','checkpoint'])
        self.assertEqual(run_post_update(h,native_head='d'*40,desired_files=desired,execute=True)['result'],'NO_CHANGE')
    def test_approval_required(self):
        h=FakeHost()
        with self.assertRaisesRegex(ValueError,'EXECUTION_APPROVAL_REQUIRED'): run_post_update(h,native_head='d'*40,desired_files=h.files)
        self.assertEqual(h.calls,[])
    def test_source_readback_failure_blocks_checkpoint(self):
        h=FakeHost(); h.publish_backup_source=lambda *a,**k: None
        with self.assertRaises(ValueError): run_post_update(h,native_head='d'*40,desired_files=h.files,execute=True)
        self.assertEqual(h.checkpoint,{})
    def test_cost_gate(self):
        h=FakeHost(); h.additional_cost=lambda:1
        with self.assertRaisesRegex(ValueError,'COST_GATE'): run_post_update(h,native_head='d'*40,desired_files=h.files,execute=True)
        self.assertEqual(h.calls,[])
