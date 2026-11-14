from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sunocleanser import __version__
from sunocleanser.suno.pipeline import (
    InvalidInputError,
    ProcessingParams,
    process_suno_wav,
    validate_output_paths,
    wav_output_paths,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="suno-clean",
        description="Suno adaptive spectral denoise with phase-cancel verification.",
    )
    parser.add_argument("input_wav", type=Path, nargs="+", help="Source WAV or MP3 file(s); several files = batch")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: same folder as input)",
    )
    parser.add_argument("--title", type=str, default=None, help="Song title for output filenames")
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Write JSON processing report to this path",
    )
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop", type=int, default=512)
    parser.add_argument("--quiet-fraction", type=float, default=0.12)
    parser.add_argument("--bass-cut", type=float, default=350.0, help="Below this Hz: untouched (default 350)")
    parser.add_argument("--oversubtraction", type=float, default=1.2)
    parser.add_argument(
        "--threshold-db",
        type=float,
        default=-60.0,
        help="Max allowed phase-cancel error in dBFS (default -60)",
    )
    parser.add_argument("--quiet", action="store_true", help="Do not print the full JSON report")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _report_path(input_path: Path, args: argparse.Namespace) -> Path:
    if args.report is not None:
        return args.report
    destination = args.out_dir if args.out_dir is not None else input_path.parent
    return destination / f"{input_path.stem}.report.json"


def _process_one(input_path: Path, args: argparse.Namespace, batch: bool) -> int:
    if not input_path.is_file():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    report_path = _report_path(input_path, args)

    try:
        params = ProcessingParams(
            n_fft=args.n_fft,
            hop_length=args.hop,
            quiet_fraction=args.quiet_fraction,
            bass_cut_hz=args.bass_cut,
            oversubtraction=args.oversubtraction,
            reconstruction_threshold_db=args.threshold_db,
        )
        result = process_suno_wav(
            input_path=input_path,
            out_dir=args.out_dir,
            title=None if batch else args.title,
            params=params,
            report_path=report_path,
        )
    except ImportError as exc:
        print(
            "Error: required audio libraries are not available. "
            "Activate conda env `sunocleanser` and install dependencies.",
            file=sys.stderr,
        )
        print(exc, file=sys.stderr)
        return 2
    except InvalidInputError as exc:
        print(f"Invalid input ({input_path.name}): {exc}", file=sys.stderr)
        return 5
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        print(json.dumps({"report_path": str(report_path)}, indent=2))
        return 3
    except Exception as exc:  # noqa: BLE001
        # Keep unexpected processing errors inside the user-facing boundary.
        print(f"Processing failed ({input_path.name}): {exc}", file=sys.stderr)
        return 4

    if not args.quiet:
        print(json.dumps(result.report, indent=2))
    print(f"Wrote: {result.clean_path}")
    print(f"Wrote: {result.noise_path}")
    print(f"Report: {report_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    inputs: list[Path] = args.input_wav
    batch = len(inputs) > 1
    if batch and (args.report is not None or args.title is not None):
        print("Error: --report and --title cannot be used with several input files.", file=sys.stderr)
        return 5

    if batch:
        try:
            outputs: list[Path] = []
            for path in inputs:
                if path.is_file():
                    outputs.extend(wav_output_paths(path, args.out_dir, None))
                    outputs.append(_report_path(path, args))
            validate_output_paths(inputs, outputs)
        except InvalidInputError as exc:
            print(f"Invalid input (batch): {exc}", file=sys.stderr)
            return 5
        except (OSError, RuntimeError) as exc:
            print(f"Cannot validate batch paths: {exc}", file=sys.stderr)
            return 4

    codes = [_process_one(path, args, batch) for path in inputs]
    failed = [c for c in codes if c != 0]
    if batch:
        print(f"Batch: {len(codes) - len(failed)}/{len(codes)} succeeded.")
    return max(codes) if failed else 0


if __name__ == "__main__":
    sys.exit(main())
