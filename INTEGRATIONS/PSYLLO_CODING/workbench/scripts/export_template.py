#!/usr/bin/env python3
"""Exportiert die aktuelle Intelligent UI in ein neues projektneutrales Verzeichnis."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def export(target: Path) -> None:
    renderer = (ROOT / "scripts" / "render_ui.py").read_text(encoding="utf-8")
    original = 'DEFAULT_HANDOFF_FORMAT = "coding-profi"'
    if renderer.count(original) != 1:
        raise ValueError("Projektvorlage: Handoff-Format ist nicht eindeutig")
    target.mkdir(parents=False, exist_ok=False)
    try:
        shutil.copytree(ROOT / "assets", target / "assets")
        (target / "scripts").mkdir()
        neutral = renderer.replace(original, 'DEFAULT_HANDOFF_FORMAT = "neutral"', 1)
        (target / "scripts" / "render_ui.py").write_text(neutral, encoding="utf-8")
        shutil.copyfile(ROOT / "template" / "README.md", target / "README.md")
        shutil.copyfile(ROOT / "template" / "view.example.json", target / "view.example.json")
    except Exception:
        shutil.rmtree(target)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="neues Unterverzeichnis in einem bestehenden Elternverzeichnis")
    args = parser.parse_args()
    export(args.target)
    print(json.dumps({"template": str(args.target.resolve()), "renderer": "scripts/render_ui.py"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
