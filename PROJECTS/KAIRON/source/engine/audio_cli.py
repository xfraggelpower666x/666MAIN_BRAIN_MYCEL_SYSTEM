"""666TDI R0.8 · Local audio feedback CLI."""
import argparse,json
from . import audio_feedback as a

def main():
    cli=argparse.ArgumentParser(description='666TDI Causal Audio Feedback (local only)')
    sub=cli.add_subparsers(dest='command',required=True)
    m=sub.add_parser('measure');m.add_argument('audio')
    c=sub.add_parser('compare');c.add_argument('track_id');c.add_argument('renderer');c.add_argument('audio');c.add_argument('--stem',action='append',default=[],help='role=/path/to/audio.wav');c.add_argument('--record',action='store_true')
    v=sub.add_parser('review');v.add_argument('track_id');v.add_argument('report_id');v.add_argument('cause');v.add_argument('reviewer');v.add_argument('note')
    sub.add_parser('rehydrate')
    args=cli.parse_args()
    if args.command=='measure':output=a.measure(args.audio)
    elif args.command=='compare':
        stems={}
        for spec in args.stem:
            if '=' not in spec:cli.error('stem format role=path')
            name,path=spec.split('=',1);stems[name]=path
        output=a.compare(args.track_id,args.renderer,args.audio,stems)
        if args.record:output={'report':output,'recording':a.record(output)}
    elif args.command=='review':output=a.review(args.track_id,args.report_id,args.cause,args.reviewer,args.note)
    else:output=a.rehydrate()
    print(json.dumps(output,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
