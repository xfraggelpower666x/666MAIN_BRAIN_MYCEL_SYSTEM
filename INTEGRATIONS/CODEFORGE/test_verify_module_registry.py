import unittest

from verify_module_registry import verify


class ModuleRegistryTests(unittest.TestCase):
    def test_legacy_registration_is_inert(self):
        master = "MOD-ID: MOD-START-001\nLEGACY-MOD-ID: MOD-START-001\n"
        report = verify(master, "001. MOD-START-001\n")
        self.assertEqual(report["status"], "MODULE_REGISTRY_MATCH")
        self.assertEqual(report["legacy_definition_count"], 1)

    def test_unregistered_bare_declaration_fails_despite_matching_counts(self):
        master = "MOD-ID: MOD-START-001\nMOD-RECOVERY-001\n"
        report = verify(master, "001. MOD-START-001\n")
        self.assertEqual(report["status"], "MODULE_REGISTRY_MISMATCH")
        self.assertEqual(report["bare_module_ids"], ["MOD-RECOVERY-001"])

    def test_duplicates_and_set_differences(self):
        master = "MOD-ID: MOD-START-001\nMOD-ID: MOD-START-001\n"
        registry = "001. MOD-RECOVERY-001\n002. MOD-RECOVERY-001\n"
        report = verify(master, registry)
        self.assertEqual(report["unregistered_active"], ["MOD-START-001"])
        self.assertEqual(report["missing_active"], ["MOD-RECOVERY-001"])
        self.assertEqual(report["duplicate_active"], ["MOD-START-001"])
        self.assertEqual(report["duplicate_registry"], ["MOD-RECOVERY-001"])

    def test_missing_declarations_are_invalid_input(self):
        for master, registry in [("", "001. MOD-START-001"), ("MOD-ID: MOD-START-001", "")]:
            with self.subTest(master=master, registry=registry), self.assertRaises(ValueError):
                verify(master, registry)


if __name__ == "__main__":
    unittest.main()
