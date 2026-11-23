"""Safe RGB preview CLI; does not access firmware, USB or real LEDs."""
import argparse
import json
from .rgb_layers import RGBPreview


def main(argv=None):
    parser = argparse.ArgumentParser(description='Keyboard RGB priority preview (NO hardware writes)')
    parser.add_argument('--layer', type=int, choices=(0, 1, 2, 3), default=0)
    parser.add_argument('--caps', action='store_true')
    parser.add_argument('--units', type=int, default=2)
    parser.add_argument('--sync', action='store_true')
    parser.add_argument('--unit-index', type=int, default=0)
    args = parser.parse_args(argv)
    try:
        sim = RGBPreview(args.units, args.sync)
        frames = sim.update(args.unit_index, (args.layer,), args.caps)
    except (ValueError, IndexError) as exc:
        parser.error(str(exc))
    print(json.dumps({'mode': 'simulation', 'synchronized': args.sync, 'frames': [dict(hex=f.hex, source=f.source, layer=f.layer) for f in frames]}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
