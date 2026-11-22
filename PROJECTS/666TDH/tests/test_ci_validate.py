"""Negative Safety-Gates des nativen TDH-CI-Entrypoints."""
import pathlib
import sys
import unittest
from unittest.mock import Mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import ci_validate as ci


class TDHNativeCIGates(unittest.TestCase):
    def test_root_identity_rejects_foreign_location(self):
        with self.assertRaisesRegex(RuntimeError, "nicht im nativen"):
            ci.check_checkout(pathlib.Path('/tmp/some-other-project'), pathlib.Path('/tmp'), '0'*40)

    def test_sha_lease_rejects_changed_head(self):
        with self.assertRaisesRegex(RuntimeError, "READBACK_PENDING"):
            ci.check_checkout(pathlib.Path('/tmp/repo/PROJECTS/666TDH'),
                              pathlib.Path('/tmp/repo'), '0'*40, '1'*40)

    def test_pass_count_requires_proof(self):
        self.assertEqual(ci.successful_test_count('Ran 29 tests in 2.0s\n\nOK\n', 0), 29)
        with self.assertRaisesRegex(RuntimeError, "fehlgeschlagen"):
            ci.successful_test_count('Ran 29 tests in 2.0s\n\nFAILED (failures=1)', 1)
        with self.assertRaisesRegex(RuntimeError, "Tests fehlen"):
            ci.successful_test_count('Ran 27 tests in 2.0s\n\nOK', 0)

    def test_host_and_child_guards_fail_closed(self):
        class FakeCurrent:
            pointer = {"authority":"REPOSITORY_PROJECT", "files":{"a":"hash"},
                       "repo_policy_revision":{"revision":"R1"},
                       "repo_capability_revision":{"revision":"R3"},
                       "release":"v1.15.0"}
            registry = {"children": {k:{"source_identity": "UNRESOLVED_HOLD" if k in ("FSE", "SHACHIVITI") else "OK"}
                                     for k in ci.EXPECTED_CHILDREN}}
        good={"status":"VERIFIZIERT_LOCAL", "native_id":"666TRACKHUB-001", "native_release":"v1.15.0",
              "children":list(ci.EXPECTED_CHILDREN), "daemon_commands":9,
              "current_manifest_count":1,"chat_host_acceptance":"OPEN_NOT_VERIFIED"}
        self.assertEqual(ci.check_native(good,FakeCurrent())["manifest_sha256_bindings_verified"],1)
        with self.assertRaisesRegex(RuntimeError, "Host-PASS"):
            ci.check_native(dict(good,chat_host_acceptance="PASS"),FakeCurrent())
        with self.assertRaisesRegex(RuntimeError, "Child-Registry"):
            ci.check_native(dict(good,children=["TD"]),FakeCurrent())


if __name__ == "__main__":
    unittest.main()
