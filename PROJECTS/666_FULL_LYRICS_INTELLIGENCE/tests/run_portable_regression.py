"""Run R03 regression without inventing or publishing the private R02 database."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
private_fixture = root / "legacy_r02" / "app" / "lyrics_library.db"
suite = unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_engine.py")

def walk(items):
    for item in items:
        if isinstance(item, unittest.TestSuite):
            yield from walk(item)
        else:
            yield item

all_tests = list(walk(suite))
if not private_fixture.is_file():
    selected = [test for test in all_tests if not test.id().endswith("test_legacy_readonly")]
    print("PRIVATE_LEGACY_FIXTURE_MISSING: read-only R02 migration test NOT RUN")
else:
    selected = all_tests

result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
print(f"PUBLIC_REGRESSION: {result.testsRun}/{len(selected)} executed; private_legacy_fixture={'present' if private_fixture.is_file() else 'missing'}")
sys.exit(0 if result.wasSuccessful() else 1)
