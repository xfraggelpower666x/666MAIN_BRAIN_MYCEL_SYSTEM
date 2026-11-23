"""Read-only Windows keyboard lock indicators."""
import argparse
import json
from .lock_indicator import LockIndicator, WindowsLockReader, PreviewLockReader, display_text


def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only virtual Caps/Num/Scroll indicators")
    p.add_argument("--order", default="NCS", help="N/C/S ordering, subset accepted")
    p.add_argument("--preview", action="store_true", help="Use simulated (all-off) lock states")
    p.add_argument("--json", action="store_true", help="JSON output")
    args = p.parse_args(argv)
    try:
        reader = PreviewLockReader() if args.preview else WindowsLockReader()
        state = LockIndicator(reader, args.order.upper()).poll()
    except (OSError, ValueError) as exc:
        p.error(str(exc))
    print(json.dumps({led: on for led, on in state}) if args.json else display_text(state))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
