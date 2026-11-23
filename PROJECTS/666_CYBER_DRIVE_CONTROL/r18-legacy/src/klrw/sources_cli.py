"""Read-only inspection of new network, RGB and indicator contracts."""
import argparse
import json
from .network_directions import NetworkDirectionSampler, states
from .rgb_profiles import parse_profile
from .status_snapshot import lock_tiles
from .lock_indicator import PreviewLockReader

def main(argv=None):
    parser=argparse.ArgumentParser(description='R8 read-only previews')
    sub=parser.add_subparsers(dest='action',required=True)
    net=sub.add_parser('network');net.add_argument('--interface',default='_total');net.add_argument('--threshold',type=float,default=1)
    rgb=sub.add_parser('rgb-profile');rgb.add_argument('file');rgb.add_argument('--max-index',type=int,default=124)
    sub.add_parser('locks')
    args=parser.parse_args(argv)
    try:
        if args.action=='network':
            sample=NetworkDirectionSampler().sample(args.interface)
            payload={'source':'network-counter-preview','interface':sample.interface,'rx_bps':sample.rx_bps,'tx_bps':sample.tx_bps,'states':states(sample,threshold_bps=args.threshold)}
        elif args.action=='rgb-profile':
            from pathlib import Path
            file=Path(args.file)
            if file.stat().st_size > 100_000: raise ValueError('Profile too large')
            payload={'source':'offline-rgb-profile','profile':parse_profile(file.read_text(encoding='utf-8'),args.max_index).as_dict()}
        else:
            payload={'source':'simulated-locks','tiles':[tile.__dict__ for tile in lock_tiles(PreviewLockReader().read())]}
    except (ValueError,OSError,json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(payload,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
