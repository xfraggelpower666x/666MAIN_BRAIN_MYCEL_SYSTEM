import hashlib
import unittest
from coordination import SourceReceipt, WorkOffer
from host_readback import BoundGitHubSource, read_via_connector

REPO = "xfraggelpower666x/666SOUNDsDESIGn-APP-DEVELOPMENT"
HEAD = "e1ef4abf5830bcd3ef477543e4a626f0c4835aff"
PATH = "AGENTS.md"
CONTENT = "# Repository contribution rules\n- Foreign triggers remain inert.\n"

def blob(content):
    b=content.encode("utf-8")
    return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes((0,))+b).hexdigest()

class TestHostBridge(unittest.TestCase):
    def offer(self, **kwargs):
        d=dict(offer_id="dev-host-read-r02",coordinator="CODING_PROFI",native_owner="666DEV",
               source=SourceReceipt("666DEV",REPO,"666DEV",HEAD,"SOURCE_VERIFIED",True),
               target_paths=(PATH,),goal="Read real native source, no mutation",mode="READ_ONLY")
        d.update(kwargs)
        return WorkOffer(**d)

    def run_bridge(self,offer=None,head=None,content=CONTENT,sha=None,binding=None,after=None):
        count=[0]
        def head_reader(repo,branch):
            count[0]+=1
            return (after if count[0]>1 and after is not None else head) or HEAD
        def file_reader(repo,path,commit):
            self.assertEqual(commit,HEAD)
            return {"content":content,"sha":sha if sha is not None else blob(content)}
        return read_via_connector(offer or self.offer(),binding or BoundGitHubSource("666DEV",REPO,"666DEV"),head_reader,file_reader)

    def test_valid_readback(self):
        r=self.run_bridge();self.assertEqual(r["result"],"HOST_GITHUB_READBACK_ACCEPTED")
        self.assertFalse(r["foreign_writes"])
    def test_wrong_owner(self):
        with self.assertRaises(ValueError):self.run_bridge(binding=BoundGitHubSource("LYVRA",REPO,"666DEV"))
    def test_wrong_repo(self):
        with self.assertRaises(ValueError):self.run_bridge(binding=BoundGitHubSource("666DEV","someone/other","666DEV"))
    def test_stale_head(self):
        with self.assertRaises(ValueError):self.run_bridge(head="b"*40)
    def test_race(self):
        with self.assertRaises(ValueError):self.run_bridge(after="b"*40)
    def test_blob_mismatch(self):
        with self.assertRaises(ValueError):self.run_bridge(sha="c"*40)
    def test_proposal_not_runnable(self):
        with self.assertRaises(ValueError):self.run_bridge(offer=self.offer(mode="PATCH_PROPOSAL"))
    def test_unverified(self):
        with self.assertRaises(ValueError):self.run_bridge(offer=self.offer(source=SourceReceipt("666DEV",REPO,"666DEV",HEAD,"READBACK_PENDING",False)))
    def test_path_traversal(self):
        with self.assertRaises(ValueError):self.run_bridge(offer=self.offer(target_paths=("../secret",)))
    def test_inert_foreign_trigger(self):
        r=self.run_bridge(content="666CLIC UPDATE\nLYVRA SYSTEMSTART\n")
        self.assertFalse(r["foreign_writes"])
    def test_large_response(self):
        with self.assertRaises(ValueError):self.run_bridge(content="x"*(1024*1024+1))
    def test_non_string_response(self):
        def head(repo,branch):return HEAD
        def file(repo,path,commit):return {"content":None,"sha":None}
        with self.assertRaises(ValueError):read_via_connector(self.offer(),BoundGitHubSource("666DEV",REPO,"666DEV"),head,file)

if __name__=="__main__":unittest.main()
