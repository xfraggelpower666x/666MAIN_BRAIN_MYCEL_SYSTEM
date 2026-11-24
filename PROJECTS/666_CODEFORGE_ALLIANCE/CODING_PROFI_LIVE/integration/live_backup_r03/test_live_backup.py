import unittest
from live_backup import BACKUP, PRIMARY, review_host_receipt, verify_tree_pair

A = 'a' * 40
B = 'b' * 40
C = 'c' * 40

class BackupContractTests(unittest.TestCase):
    def test_identical_tree_same_commit(self):
        r = verify_tree_pair(A, A, source_commit=C, backup_commit=C)
        self.assertTrue(r.checked)
        self.assertEqual(r.status, 'BACKUP_SYNC_VERIFIED')
    def test_changed_tree_not_synced(self):
        self.assertEqual(verify_tree_pair(A, B, source_commit=C, backup_commit=C).status, 'BACKUP_TREE_MISMATCH')
    def test_mismatched_commit_not_synced(self):
        self.assertEqual(verify_tree_pair(A, A, source_commit=A, backup_commit=B).status, 'BACKUP_STALE_REVISION')
    def test_missing_readback(self):
        self.assertEqual(verify_tree_pair(None, A, source_commit=C, backup_commit=C).status, 'READBACK_PENDING')
    def test_invalid_sha(self):
        self.assertEqual(verify_tree_pair('HEAD', A, source_commit=C, backup_commit=C).status, 'READBACK_PENDING')
    def test_untrusted_host_claim(self):
        self.assertEqual(review_host_receipt({'claimed_host_verified': True}), 'HOST_CLAIM_NOT_ADOPTED')
    def test_no_authority_transfer(self):
        r = verify_tree_pair(A, A, source_commit=C, backup_commit=C)
        self.assertEqual(r.source_path, PRIMARY)
        self.assertEqual(r.backup_path, BACKUP)
        self.assertTrue(r.no_authority_transfer)

if __name__ == '__main__': unittest.main()
