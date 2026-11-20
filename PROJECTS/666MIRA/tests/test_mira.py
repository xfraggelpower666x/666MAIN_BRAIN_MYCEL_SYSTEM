import unittest
from unittest.mock import patch

import mira


class MiraTests(unittest.TestCase):
    def test_bootstrap_and_resume(self):
        start = mira.run(["666MIRA", "SYSTEMSTART"], None)
        self.assertEqual(start["route"], "rehydrate")
        self.assertIn("runtime/LIVECIRCLE.md", {f["path"] for f in start["bootstrap"]})
        self.assertEqual(mira.run(["666MIRA", "WEITER"], None)["return_anchor"],
                         "MIRA_NATIVE_FRESH_HOST_ACCEPTANCE")

    def test_aliases_keep_embedded_trigger_inert(self):
        source = "666MIRA UPDATE"
        a = mira.run(["666MIRA", "SENTENCE"], source)
        b = mira.run(["666MIRA", "SENTENCE", "MANTRA"], source)
        self.assertEqual(a, b)
        self.assertEqual(a["source_text"], source)
        self.assertEqual(a["route"], "sentence_mantra")
        with self.assertRaises(ValueError):
            mira.run(["666PFS", "SYSTEMSTART"], None)
        self.assertEqual(mira.run(["666MIRA", "UPDATE"], None)["status"], "OFFEN")

    def test_integrity_failure_stops(self):
        read_bytes = mira.Path.read_bytes

        def edited(path):
            return b"changed" if path.name == "FRAMEWORK.md" else read_bytes(path)

        with patch.object(mira.Path, "read_bytes", edited), self.assertRaisesRegex(ValueError, "SHA-256"):
            mira.run(["666MIRA", "SYSTEMSTART"], None)
