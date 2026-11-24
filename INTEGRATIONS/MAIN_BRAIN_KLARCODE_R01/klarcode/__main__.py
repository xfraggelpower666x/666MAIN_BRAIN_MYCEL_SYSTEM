"""Command line entrypoint: python -m klarcode <command>..."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .engine import GateError, Manager


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='666 MAIN BRAIN Klarcode candidate R01')
    p.add_argument('--workspace', type=Path, required=True, help='Working directory containing PROJECTS/')
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('register', help='Register new MINI or existing NATIVE_DELEGATED without takeover')
    a.add_argument('--project', required=True)
    a.add_argument('--owner', required=True)
    a.add_argument('--kind', required=True, choices=('LOCAL_MINI','NATIVE_DELEGATED'))
    a.add_argument('--root')
    a.add_argument('--native-pointer')
    for cmd in ('status','rehydrate'):
        a = sub.add_parser(cmd)
        a.add_argument('--project', required=True)
    a = sub.add_parser('save', help='Immutable clearcode release for LOCAL_MINI ONLY')
    a.add_argument('--project', required=True)
    a.add_argument('--owner', required=True)
    a.add_argument('--source', type=Path, required=True)
    a.add_argument('--expected-pointer', required=True)
    a.add_argument('--mainbrain-observed-head')
    a.add_argument('--mainbrain-current-head')
    a.add_argument('--mainbrain-pointer-present', action='store_true')
    a = sub.add_parser('handoff', help='Read-only prepared native-owner handoff')
    a.add_argument('--project', required=True)
    a.add_argument('--action', default='REVALIDATE_CODE_SNAPSHOT')
    a = sub.add_parser('whole-check', help='Determine whether MAIN BRAIN whole must be revalidated')
    a.add_argument('--observed-head', required=True)
    a.add_argument('--current-head', required=True)
    a.add_argument('--whole-pointer-present', action='store_true')
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    man = Manager(args.workspace)
    try:
        if args.command == 'register':
            result = man.register(args.project, args.owner, args.kind, root=args.root, native_pointer=args.native_pointer)
        elif args.command in ('status','rehydrate'):
            result = man.status(args.project)
            if args.command == 'rehydrate':
                if result['mode'] == 'NATIVE_DELEGATED':
                    result['rehydration'] = 'DEFER_TO_NATIVE_SYSTEM_OWNER'
                else:
                    result['rehydration'] = 'SOURCE_REHYDRATED_NOT_HOST_EXECUTED'
        elif args.command == 'save':
            if bool(args.mainbrain_observed_head) != bool(args.mainbrain_current_head):
                raise GateError('Whole HEAD observation requires both previous and current heads')
            result = man.save(args.project,args.source,owner=args.owner,expected_pointer=args.expected_pointer)
            if args.mainbrain_observed_head:
                result['whole_delta'] = man.whole_delta(args.mainbrain_observed_head,args.mainbrain_current_head,
                                                        whole_pointer_present=args.mainbrain_pointer_present)
        elif args.command == 'handoff':
            result = man.handoff(args.project,desired_action=args.action)
        else:
            result = man.whole_delta(args.observed_head,args.current_head,whole_pointer_present=args.whole_pointer_present)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (GateError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({'status':'BLOCKIERT','reason':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
