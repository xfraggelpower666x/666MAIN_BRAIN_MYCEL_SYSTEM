"""Command-line entry point for the isolated R03 stem analyzer."""
from __future__ import annotations

import argparse
import json
import sys

from src.stem_masking import AnalysisError, analyze_stems, parse_stem_spec, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bounded psychoacoustic stem overlap analysis (R03)")
    parser.add_argument("--input", required=True, help="Folder containing PCM WAV stem files")
    parser.add_argument("--stem", action="append", required=True, type=parse_stem_spec, metavar="ROLE=FILE",
                        help="Explicit role mapping; repeat for kick, bass, vocal, acid, guitar, fx")
    parser.add_argument("--output", help="Optional output folder; writes stem-analysis-r03.json")
    parser.add_argument("--force", action="store_true", help="Allow replacing an existing report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = analyze_stems(args.input, args.stem)
        if args.output:
            path = write_report(report, args.output, args.input, force=args.force)
            print(json.dumps({"status": report["status"], "report": str(path)}, ensure_ascii=False))
        else:
            print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (AnalysisError, OSError, ValueError) as exc:
        print(f"BLOCKIERT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
