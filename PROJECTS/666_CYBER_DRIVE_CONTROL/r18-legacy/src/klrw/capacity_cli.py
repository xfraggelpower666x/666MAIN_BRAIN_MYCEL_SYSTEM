"""Local, read-only filesystem capacity CLI with optional JSON output."""
import argparse
from dataclasses import asdict
import json
from .volumes import VolumeSampler

def main(argv=None):
    p=argparse.ArgumentParser(description="KLRW filesystem capacity (no network, no hardware writes)")
    p.add_argument("--warning",type=float,default=80.)
    p.add_argument("--critical",type=float,default=95.)
    p.add_argument("--include-remote",action="store_true",help="explicitly allow reading network volume capacities")
    p.add_argument("--json",action="store_true",help="print structured JSON")
    a=p.parse_args(argv)
    try:
        items,failures=VolumeSampler(warning=a.warning,critical=a.critical,include_remote=a.include_remote).sample()
    except ValueError as exc:
        p.error(str(exc))
    if a.json:
        print(json.dumps({"volumes":[asdict(v) for v in items],"errors":failures},ensure_ascii=False,sort_keys=True))
    else:
        for v in items:
            print(f"{v.mountpoint}: free {v.free_bytes/(1024**3):.1f} GiB, used {v.used_percent:.1f}%, {v.status}")
        for location,reason in failures.items():
            print(f"{location}: unavailable ({reason})")
    return 0

if __name__=="__main__": raise SystemExit(main())
