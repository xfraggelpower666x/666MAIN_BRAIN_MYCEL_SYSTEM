"""Portable CLI: python -m engine.cli <command> ..."""
import argparse,json
from pathlib import Path
from . import portable as p

def main():
    a=argparse.ArgumentParser(description='666TDI portable track intelligence')
    s=a.add_subparsers(dest='command',required=True)
    for cmd in ('systemstart','status','rehydrate','handoff','help'):s.add_parser(cmd)
    c=s.add_parser('create');c.add_argument('intent_json')
    c=s.add_parser('analyze');c.add_argument('track_id')
    c=s.add_parser('compile');c.add_argument('track_id');c.add_argument('renderer')
    c=s.add_parser('feedback');c.add_argument('track_id');c.add_argument('renderer');c.add_argument('observation');c.add_argument('--evidence',default='USER_REPORTED');c.add_argument('--artifact')
    args=a.parse_args();command=args.command
    if command=='help':out=p.load(p.ROOT/'registry'/'triggers.json')
    elif command=='systemstart':out=p.start()
    elif command in ('status','rehydrate'):out=p.rehydrate()
    elif command=='create':out=p.create_track(json.loads(Path(args.intent_json).read_text(encoding='utf-8')))
    elif command=='analyze':out=p.analyze(p.load(p.DATA/'tracks'/f'{args.track_id}.json'))
    elif command=='compile':out=p.compiler(p.load(p.DATA/'tracks'/f'{args.track_id}.json'),args.renderer)
    elif command=='feedback':out=p.record_feedback(args.track_id,args.renderer,args.observation,args.evidence,args.artifact)
    elif command=='handoff':out=p.handoff()
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
