import unittest
from update_coordinator import *

class R22Tests(unittest.TestCase):
    def setUp(self):
        self.files={'plugin.json':b'{}','.codex-plugin/plugin.json':b'{}','skills/test/SKILL.md':b'original'}
        self.native=dict(system_id=SYSTEM,repository=REPO,branch=BRANCH,head='a'*40,readback_verified=True,regression_passed=True,recovery_verified=True)
        self.target=dict(system_id=SYSTEM,repository=REPO,branch=BRANCH,path=TARGET,checkpoint=CHECKPOINT,authority=False,plugin_id=PLUGIN,cost_limit=0)
        self.live=dict(plugin_id=PLUGIN,release_id='old',files=self.files)
    def decide(self,desired=None,backup=None,**kw):
        return plan(native=self.native,desired_files=desired or self.files,live=self.live,backup=backup or {},target=self.target,**kw)
    def test_no_change_no_release(self):
        p=self.decide(backup=dict(files=inventory(self.files),release_id='old',readback_verified=True))
        self.assertEqual(p['next_action'],'NO_CHANGE')
    def test_missing_backup(self):
        self.assertEqual(self.decide()['next_action'],'BACKUP_CAS')
    def test_release_change_and_readback(self):
        desired=dict(self.files);desired['skills/test/SKILL.md']=b'new'
        p=self.decide(desired)
        self.assertEqual(p['next_action'],'RELEASE_CAS')
        new=dict(self.live,release_id='new',files=desired)
        v=verify_release(p,new,previous_release_id='old')
        self.assertEqual(len(backup_entries(v,new,expected_head='a'*40,observed_head='a'*40,recovery_verified=True)),3)
        self.assertEqual(verify_backup(v,desired,dict(v,authority=False))['status'],'BACKUP_VERIFIED')
    def test_cas_conflict(self):
        p=self.decide()
        with self.assertRaises(ValueError): verify_release(p,self.live,previous_release_id='wrong')
        v=verify_release(p,self.live,previous_release_id='old')
        with self.assertRaises(ValueError): backup_entries(v,self.live,expected_head='a'*40,observed_head='b'*40,recovery_verified=True)
    def test_secret_and_scope(self):
        with self.assertRaises(ValueError): inventory(dict(self.files,**{'skills/test/SKILL.md':b'password="abcdefghijklmnop"'}))
        with self.assertRaises(ValueError): self.decide(paid_cost=1)
        self.target['path']='PROJECTS/OTHER/'
        with self.assertRaises(ValueError): self.decide()
    def test_deletion_and_unverified_native(self):
        desired=dict(self.files);del desired['skills/test/SKILL.md']
        with self.assertRaises(ValueError): self.decide(desired)
        self.native['readback_verified']=False
        with self.assertRaises(ValueError): self.decide()
