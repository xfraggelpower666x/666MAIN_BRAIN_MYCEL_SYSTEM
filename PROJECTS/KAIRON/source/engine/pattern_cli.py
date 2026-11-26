"""R0.7 local pattern assessment; no network, costs or automatic promotion."""
import argparse,json
from . import pattern_relations as r

def main():
    p=argparse.ArgumentParser(description='666TDI track-local pattern relations')
    s=p.add_subparsers(dest='operation',required=True)
    a=s.add_parser('assess');a.add_argument('track_id');a.add_argument('--include-presets',action='store_true')
    b=s.add_parser('attach-reviewed');b.add_argument('track_id');b.add_argument('candidate_id');b.add_argument('--reason',required=True);b.add_argument('--reviewer',required=True);b.add_argument('--functions',required=True,help='comma separated semantic function IDs')
    z=p.parse_args()
    if z.operation=='assess': x=r.assess(z.track_id,include_presets=z.include_presets)
    else:x=r.attach_reviewed(z.track_id,z.candidate_id,z.reason,z.reviewer,[t.strip() for t in z.functions.split(',') if t.strip()])
    print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
