"""CLI for local 666TDI relational intelligence; no remote operations."""
from . import relational as r
import argparse,json

def main():
    a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True)
    for cmd in ('build','inspect','assess'):
        s.add_parser(cmd).add_argument('track_id')
    s.add_parser('rehydrate')
    x=a.parse_args()
    result={'build':lambda:r.build(x.track_id),'inspect':lambda:r.inspect(x.track_id),'assess':lambda:r.assess(x.track_id),'rehydrate':r.rehydrate}[x.cmd]()
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
