"""Nur additive Befehle. Vorhandene `python -m engine.cli` bleibt unverändert."""
import argparse,json
from . import portable as p, evolution as e

def main():
    arg=argparse.ArgumentParser(description='666TDI v2.5 zusätzliche lokale Funktionen')
    sub=arg.add_subparsers(dest='command',required=True)
    for name in ('status','character','modules'):sub.add_parser(name)
    x=sub.add_parser('tension');x.add_argument('events_json',help='JSON array of EXPECT/RESOLVE event objects')
    x=sub.add_parser('temporal-feedback');x.add_argument('track_id');x.add_argument('layer');x.add_argument('text');x.add_argument('--supersedes');x.add_argument('--creator-retraction',action='store_true')
    x=sub.add_parser('aperture');x.add_argument('energy');x.add_argument('width');x.add_argument('focus');x.add_argument('edge');x.add_argument('trajectory')
    x=sub.add_parser('conflict');x.add_argument('foreground');x.add_argument('competing')
    args=arg.parse_args()
    if args.command=='status':out=e.comprehensive_status()
    elif args.command=='character':out=e.character_readback()
    elif args.command=='modules':out=p.load(p.ROOT/'registry'/'additive_modules.json')
    elif args.command=='tension':out=e.predictive_tension(json.loads(args.events_json))
    elif args.command=='temporal-feedback':out=e.temporal_feedback(args.track_id,args.layer,args.text,context={'explicit_creator_retraction':True} if args.creator_retraction else None,supersedes=args.supersedes)
    elif args.command=='aperture':out=e.aperture_geometry(args.energy,args.width,args.focus,args.edge,args.trajectory)
    elif args.command=='conflict':out=e.conflict_candidates(args.foreground,args.competing)
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
