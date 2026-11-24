import unittest
from alliance_review import inspect_handoff, AllianceRejected


def offer():
    return dict(handoff_id="h-1",source_system_id="LYVRA_CODING_PROFI",target_system_id="LYVRA",
                native_current_ref="source only",source_revision="unverified",capability_id="review",
                task_id="t-1",read_scope=["docs"],write_scope=[],dependencies=[],
                delivery_receipt="NOT_SENT",acceptance_receipt="NOT_RECEIVED",
                evidence_refs=["source"],status="PROPOSED")

class AllianceReviewTests(unittest.TestCase):
    def test_proposal_is_never_promoted(self):
        result = inspect_handoff(offer())
        self.assertEqual(result["result"], "REVIEW_ONLY")
        self.assertFalse(result["native_current_verified"])
        self.assertFalse(result["host_dispatch_performed"])
    def test_missing_contract_field(self):
        x = offer(); del x["native_current_ref"]
        with self.assertRaisesRegex(AllianceRejected, "INVALID_HANDOFF_SHAPE"):
            inspect_handoff(x)
    def test_no_self_peer(self):
        x = offer(); x["target_system_id"] = x["source_system_id"]
        with self.assertRaisesRegex(AllianceRejected, "SELF_PEER_HANDOFF"):
            inspect_handoff(x)

if __name__ == '__main__': unittest.main()
