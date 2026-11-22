"""CLIC R07 MB-01..05 — MAIN BRAIN native acceptance fences (read-only)."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ClicR07NativeFences(unittest.TestCase):
    def test_mb01_migration_authority_preserved(self) -> None:
        pointer = read("CURRENT_POINTER.md")
        state = read("SYSTEM/CURRENT_STATE.md")
        self.assertIn("REPO_FIRST_AUTH=FALSE_UNTIL_FINAL_COMPLETION_GATE", pointer)
        self.assertIn("DRIVE_ROLE=MIGRATION_SOURCE_RECOVERY", pointer)
        self.assertIn("MIGRATION_STATE=IN_PROGRESS_UNTIL_FINAL_COMPLETION_GATE", state)
        self.assertNotIn("DRIVE_ROLE=HISTORY_ONLY\n", state)

    def test_mb02_peer_freshness_does_not_promote_peer(self) -> None:
        text = read("INTELLIGENCE/DEV/DEV_SOURCE_ADAPTER.md")
        self.assertIn("PEER_HEAD_READBACK_2026_11_22=e1ef4abf5830bcd3ef477543e4a626f0c4835aff", text)
        self.assertIn("PEER_NATIVE_AUTHORITY_ADOPTION=NOT_GRANTED", text)
        self.assertIn("ADAPTER_MODE=READ_ONLY_UNCHANGED", text)

    def test_mb03_plugin_release_is_observation_not_host_acceptance(self) -> None:
        text = read("HOST/PLUGIN_CURRENT.md")
        self.assertIn("ACCOUNT_PLUGIN_VERSION_OBSERVED=0.3.2", text)
        self.assertIn("ACCOUNT_PLUGIN_RELEASE_OBSERVED=pluginrel_6b022ac2cc108191b8eb774cac39c172", text)
        self.assertIn("RELEASE_NE_FRESH_CHAT_HOST_ACCEPTANCE=TRUE", text)

    def test_mb04_native_facet_count_and_dev_preserved(self) -> None:
        registry = json.loads(read("RUNTIME/FACET_RUNTIME_REGISTRY.json"))
        facets = registry["facets"]
        self.assertEqual(len(facets), 15)
        self.assertIn("PSYLLO.DEV", [item["id"] for item in facets])
        self.assertTrue(all(not item["independent_authority"] for item in facets))
        self.assertFalse(registry["foreign_autoactivation"])

    def test_mb05_visual_presentation_only(self) -> None:
        ui = read("UI/INTELLIGENT_UI/UI_CONTRACT.md")
        menu = json.loads(read("UI/INTELLIGENT_UI/MENU_REGISTRY.json"))
        self.assertIn("UI_NE_WRITE_AUTHORITY=TRUE", ui)
        self.assertIn("UI_NE_ROUTER=TRUE", ui)
        self.assertTrue(menu["text_fallback"])
        self.assertTrue(menu["no_unverified_triggers"])
        self.assertNotIn("666MAIN BRAIN UPDATE", [x["trigger"] for x in menu["native_actions"]])


if __name__ == "__main__":
    unittest.main()
