"""Read-only system dashboard snapshot CLI. Optional SMART only with explicit flag."""
import argparse
import json
from dataclasses import asdict
from .overview import OverviewSampler
from .health import SmartctlReader


def main(argv=None):
    p=argparse.ArgumentParser(description="KLRW multi-metric status (read-only)")
    p.add_argument("--disk", default="_total")
    p.add_argument("--smart-device", help="SMART device path, opt-in read only (requires smartctl)")
    args=p.parse_args(argv)
    obj={"overview":asdict(OverviewSampler(device=args.disk).sample())}
    if args.smart_device:
        try: obj["smart"] = asdict(SmartctlReader(enabled=True).read(args.smart_device))
        except (OSError, ValueError, RuntimeError) as ex: obj["smart_error"] = str(ex)[:200]
    print(json.dumps(obj,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
