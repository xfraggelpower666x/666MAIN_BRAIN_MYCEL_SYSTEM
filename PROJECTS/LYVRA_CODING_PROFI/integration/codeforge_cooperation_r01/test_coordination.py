import unittest
from coordination import SourceReceipt,WorkOffer,coordination_summary
SHA="a"*40
class ContractTests(unittest.TestCase):
    def source(self,**patch):
        data=dict(family="666CLIC",repository="xfraggelpower666x/666CLICPRO",branch="main",commit=SHA,status="SOURCE_VERIFIED",readback=True)
        data.update(patch)
        return SourceReceipt(**data)
    def offer(self,**patch):
        data=dict(offer_id="clic-check-01",coordinator="CODING_PROFI",native_owner="666CLIC",source=self.source(),target_paths=("src/main.py",),goal="Check interfaces",mode="READ_ONLY")
        data.update(patch)
        return WorkOffer(**data)
    def test_success(self): self.assertEqual(self.offer().decision(),"READY_FOR_READ_ONLY_COORDINATION")
    def test_pending(self): self.assertEqual(self.offer(source=self.source(repository=None,branch=None,commit=None,status="READBACK_PENDING",readback=False)).decision(),"READBACK_PENDING")
    def test_fake_verified(self):
        with self.assertRaises(ValueError): self.offer(source=self.source(readback=False)).validate()
    def test_owner(self):
        with self.assertRaises(ValueError): self.offer(native_owner="LYVRA").validate()
    def test_paths(self):
        for path in ("../secret","/absolute","foo\\\\bar","a/../b",""):
            with self.subTest(path=path),self.assertRaises(ValueError): self.offer(target_paths=(path,)).validate()
    def test_inert_trigger(self): self.assertEqual(self.offer(goal="LYVRA UPDATE as quoted data").decision(),"READY_FOR_READ_ONLY_COORDINATION")
    def test_no_write_authority(self):
        with self.assertRaises(ValueError): self.offer(user_write_authorization=True).validate()
    def test_duplicate(self):
        with self.assertRaises(ValueError): coordination_summary([self.offer(),self.offer()])
    def test_no_execution(self):
        summary=coordination_summary([self.offer(mode="PATCH_PROPOSAL")])
        self.assertFalse(summary["external_writes"])
        self.assertFalse(summary["offers"][0]["write_permitted"])
    def test_unknown(self):
        with self.assertRaises(ValueError): self.offer(native_owner="666STREAMER",source=self.source(family="666STREAMER")).validate()
    def test_invalid_sha(self):
        with self.assertRaises(ValueError): self.offer(source=self.source(commit="guess")).validate()
if __name__=="__main__": unittest.main()
