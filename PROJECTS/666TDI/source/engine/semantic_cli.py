"""Read-only CLI for 666TDI R0.9 semantic music intelligence."""
import argparse
import json
from . import portable as p
from . import semantic_intelligence as semantic

def main():
    parser = argparse.ArgumentParser(description="666TDI semantic music intelligence")
    sub = parser.add_subparsers(dest="operation", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("track_id")
    args = parser.parse_args()
    track = p.load(p.DATA / "tracks" / f"{args.track_id}.json")
    result = semantic.assess(track)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
