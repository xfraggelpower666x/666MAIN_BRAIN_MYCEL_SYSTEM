"""Regression: importer must resolve the real repository root, not PROJECTS/."""
from pathlib import Path
import ast

REPO_ROOT = Path(__file__).resolve().parents[4]
IMPORTER = Path(__file__).resolve().parents[1] / "scripts" / "R18_IMPORT_AND_VERIFY.py"


def test_importer_uses_checkout_root():
    # In a real checkout: /checkout/PROJECTS/666_CYBER_DRIVE_CONTROL/scripts/R18_IMPORT_AND_VERIFY.py
    simulated = Path("/checkout/PROJECTS/666_CYBER_DRIVE_CONTROL/scripts/R18_IMPORT_AND_VERIFY.py")
    assert simulated.parents[3] == Path("/checkout")
    assert simulated.parents[2] == Path("/checkout/PROJECTS")
    code = IMPORTER.read_text(encoding="utf-8")
    ast.parse(code)
    assert "repo=Path(__file__).resolve().parents[3]" in code
    assert "destination=Path(__file__).resolve().parents[1]/\"r18-legacy\"" in code


def test_no_cross_project_import_destination():
    project = Path("/checkout/PROJECTS/666_CYBER_DRIVE_CONTROL/scripts/R18_IMPORT_AND_VERIFY.py").parents[1]
    assert project / "r18-legacy" == Path("/checkout/PROJECTS/666_CYBER_DRIVE_CONTROL/r18-legacy")
