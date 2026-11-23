"""Read-only inspection commands for 666TDI v2.5 candidate intake."""
import argparse,json
from .source_adapters import intake_registry,candidate_catalog,match_patterns,field_audit,ace_step_intake

def main():
    p=argparse.ArgumentParser(prog='666TDI source adapters')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('inventory');sub.add_parser('catalog');sub.add_parser('ace-review')
    m=sub.add_parser('match');m.add_argument('text')
    a=sub.add_parser('count');a.add_argument('text');a.add_argument('--limit',type=int,default=1000);a.add_argument('--mode',choices=['unicode_codepoints','utf16_units','utf8_bytes'],default='unicode_codepoints')
    z=p.parse_args()
    out={'inventory':intake_registry,'catalog':candidate_catalog,'ace-review':ace_step_intake,'match':lambda:match_patterns(z.text) if z.command=='match' else None,'count':lambda:field_audit(z.text,z.limit,z.mode) if z.command=='count' else None}[z.command]()
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
