"""R03 PowerShell block planner translation. No audio mutation. See docs/PORT_R03.md."""
from dataclasses import dataclass,field
from pathlib import Path
import math,random,re
def clean_title(s):
 s=re.sub(r'^\d+[\s_.-]*','',s)
 s=re.sub(r'\s*\(\d+\)','',s)
 s=re.sub(r'\bV\d+\b|\bFINAL\b|\bMIXDOWN\b|\bTEMP\b|\bDRAFT\b','',s,flags=re.I)
 s=re.sub(r'[_-]+',' ',s)
 return re.sub(r'\s+',' ',s).strip() or s
def family_name(s): return clean_title(re.sub(r'\s*\(\d+\)','',s)).lower()
def artist_name(s):
 n=s.lower(); m=re.match(r'^\s*(.+?)\s*-\s*',n)
 if m:return m.group(1).strip()
 words=n.split()
 return ' '.join(words[:2]) if len(words)>1 else n
def energy_bucket(s):
 n=s.lower()
 if re.search('intro|ambient|soft|calm|downtempo|chill',n):return 'LOW'
 if re.search('hard|peak|pressure|freak|destroy|dark|psy|acid|rage',n):return 'HIGH'
 return 'MID'
@dataclass(frozen=True)
class Member:
 path:Path
 duration_seconds:float
 family:str
 artist:str
 energy:str
@dataclass
class Block:
 index:int
 items:list=field(default_factory=list)
 families:set=field(default_factory=set)
 total_seconds:float=0
 def append(self,m):
  self.items.append(m);self.families.add(m.family);self.total_seconds+=m.duration_seconds
 @property
 def total_tracks(self):return len(self.items)
def catalog(entries,rng=None):
 rng=rng or random.Random()
 groups={}
 for path,duration in entries:
  path=Path(path)
  if not math.isfinite(duration) or duration<0:raise ValueError('Invalid duration')
  title=path.stem;f=family_name(title)
  groups.setdefault(f,[]).append(Member(path,float(duration),f,artist_name(title),energy_bucket(title)))
 families=list(groups.values())
 for family in families:rng.shuffle(family)
 rng.shuffle(families)
 return families
def balanced_blocks(families,split_mode='MINUTES',target_minutes=180,target_tracks=40):
 if split_mode not in ('MINUTES','TRACKS','HYBRID'):raise ValueError('Unknown split mode')
 items=[m for f in families for m in f]
 if not items:return []
 secs=sum(m.duration_seconds for m in items)
 by_min=math.ceil(secs/(target_minutes*60)) if target_minutes>0 else 1
 by_tracks=math.ceil(len(items)/target_tracks) if target_tracks>0 else 1
 count=max(1,by_min if split_mode=='MINUTES' else by_tracks if split_mode=='TRACKS' else max(by_min,by_tracks))
 count=min(count,len(items))
 blocks=[Block(i+1) for i in range(count)];pointer=0
 for family in families:
  for member in family:
   placed=False
   for shift in range(count):
    idx=(pointer+shift)%count
    if member.family not in blocks[idx].families:
     blocks[idx].append(member);pointer=(idx+1)%count;placed=True;break
   if not placed:min(blocks,key=lambda b:(b.total_tracks,b.total_seconds)).append(member)
 return blocks
def smart_shuffle(items,hardcore=False):
 rem=list(items)
 if len(rem)<=2:return rem
 result=[];last_family='';last_artist='';cycle=('LOW','MID','HIGH','MID')
 while rem:
  idx=None
  if hardcore:
   wanted=cycle[len(result)%len(cycle)]
   idx=next((i for i,m in enumerate(rem) if m.family!=last_family and m.artist!=last_artist and m.energy==wanted),None)
   if idx is None:idx=next((i for i,m in enumerate(rem) if m.family!=last_family and m.artist!=last_artist),None)
  if idx is None:idx=next((i for i,m in enumerate(rem) if m.family!=last_family),0)
  chosen=rem.pop(idx);result.append(chosen);last_family=chosen.family;last_artist=chosen.artist
 return result
