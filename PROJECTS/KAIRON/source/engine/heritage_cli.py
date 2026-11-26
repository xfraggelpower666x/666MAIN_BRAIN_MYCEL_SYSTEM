"""Additive R0.4 commands, no foreign writes."""
import argparse,json
from . import heritage as h

def main():
    ap=argparse.ArgumentParser(description='666TDI v2.5 R0.4 heritage additions')
    sub=ap.add_subparsers(dest='command',required=True)
    x=sub.add_parser('style');x.add_argument('text');x.add_argument('--family')
    x=sub.add_parser('remember');x.add_argument('subject');x.add_argument('observation');x.add_argument('source_id')
    sub.add_parser('garden')
    x=sub.add_parser('mode');x.add_argument('name')
    x=sub.add_parser('character-guard');x.add_argument('text')
    args=ap.parse_args()
    if args.command=='style':out=h.style_context(args.text,args.family)
    elif args.command=='remember':out=h.memory_observe(args.subject,args.observation,args.source_id)
    elif args.command=='garden':out=h.memory_review()
    elif args.command=='mode':out=h.role_boundary(args.name)
    else:out=h.character_identity_guard(args.text)
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
