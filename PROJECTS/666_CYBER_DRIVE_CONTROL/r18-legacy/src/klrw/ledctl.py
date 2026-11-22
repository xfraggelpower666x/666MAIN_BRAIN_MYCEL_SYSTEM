"""Safe one-shot LED diagnostics; never activates hardware implicitly."""
import argparse
import json
import sys
from .manual import ManualLedController

def main(argv=None):
    p = argparse.ArgumentParser(description='Keyboard LED diagnostics (preview by default)')
    p.add_argument('led', choices=['caps','num','scroll'])
    p.add_argument('action', choices=['get','on','off'])
    p.add_argument('--hardware', action='store_true', help='Affects functional Windows LOCK state; hardware dependent')
    p.add_argument('--acknowledge-lock-change', action='store_true', help='Explicit second confirmation for hardware writes')
    p.add_argument('--keep-state', action='store_true', help='Do not restore hardware lock-key state after command')
    args = p.parse_args(argv)
    if args.hardware and sys.platform != 'win32':
        p.error('hardware mode only available on native Windows')
    if args.hardware and args.action != 'get' and not args.acknowledge_lock_change:
        p.error('hardware write requires --acknowledge-lock-change')
    if args.keep_state and (not args.hardware or args.action == 'get' or not args.acknowledge_lock_change):
        p.error('--keep-state requires an explicitly acknowledged hardware write')
    try:
        ctrl = ManualLedController(hardware=args.hardware)
        try:
            result = ctrl.state(args.led) if args.action == 'get' else ctrl.set(args.led,args.action=='on')
            print(json.dumps(vars(result)))
            # Diagnostic commands normally restore original lock state upon close.
            # keep-state intentionally leaves functional key state changed.
            if args.keep_state:
                ctrl.backend.touched.discard(args.led)
        finally:
            ctrl.close()
        return 0
    except (ValueError, RuntimeError, OSError) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
