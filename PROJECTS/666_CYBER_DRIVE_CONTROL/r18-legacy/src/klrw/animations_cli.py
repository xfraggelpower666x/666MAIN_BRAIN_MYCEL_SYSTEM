"""Safe pattern and Morse preview commands; no hardware flags by design."""
import argparse
import json
from .patterns import sequence, meter
from .morse_preview import encode
from .preview_scheduler import prepare, morse_frames


def main(argv=None):
    p = argparse.ArgumentParser(description='LED animations (simulation only)')
    sub = p.add_subparsers(dest='mode', required=True)
    a = sub.add_parser('pattern'); a.add_argument('name', choices=('chase','bounce','fill','center','pulse'))
    a.add_argument('--duration-ms', type=int, default=150)
    m = sub.add_parser('meter'); m.add_argument('value', type=float); m.add_argument('--maximum', type=float, default=100)
    s = sub.add_parser('morse'); s.add_argument('text'); s.add_argument('--unit-ms', type=int, default=120)
    s.add_argument('--led', choices=('num','caps','scroll'), default='caps')
    args = p.parse_args(argv)
    try:
        if args.mode == 'pattern': frames = sequence(args.name, args.duration_ms)
        elif args.mode == 'meter': frames = (meter(args.value, args.maximum),)
        else: frames = morse_frames(encode(args.text, args.unit_ms), args.led)
        result = prepare(frames)
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps({'destination': result.destination, 'total_ms': result.total_ms,
                      'frames': [{'states': f.states(), 'duration_ms': f.duration_ms}
                                 for f in result.frames]}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
