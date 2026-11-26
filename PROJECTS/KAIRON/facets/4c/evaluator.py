"""666TDI: optionale, rein strukturelle 4C-Prüfung ohne Audio-Pflicht."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

FOUR_C=("core","character","control","chaos")
DNA=("hook_type","rhythm_type","repeat_type","voice_mode","character_motion","chaos_pattern")

@dataclass(frozen=True)
class Finding:
    rule:str
    severity:str
    result:str
    evidence:str

def _present(track,key):
    v=(track.get("layers") or {}).get(key)
    return v is True or isinstance(v,dict) and v.get("planned") is True

def analyze(track:dict[str,Any],reference:dict[str,Any]|None=None,*,profile:str="4c_techno_candidate")->dict[str,Any]:
    """Nur die übergebene Trackplanung bewerten; niemals Daten umschreiben."""
    if not isinstance(track,dict): raise TypeError("track must be an object")
    findings=[]
    for layer in FOUR_C:
        hit=_present(track,layer)
        findings.append(Finding("4C_"+layer.upper(),"review","present" if hit else "unverified",
            "Declared by track.layers" if hit else "No affirmative layer evidence"))
    bpm=track.get("bpm")
    if isinstance(bpm,bool) or (bpm is not None and (not isinstance(bpm,(int,float)) or not 1<=bpm<=300)):
        findings.append(Finding("BPM_VALIDITY","error","invalid","BPM must be positive"))
    elif isinstance(bpm,(int,float)) and not 140<=bpm<=142:
        findings.append(Finding("BPM_PROFILE","info","profile_divergence","Historical 140-142 BPM is not global 666TDI default"))
    sections=track.get("sections",[])
    if not isinstance(sections,list): raise TypeError("sections must be a list")
    for section in sections:
        if not isinstance(section,dict):
            findings.append(Finding("SECTION_SCHEMA","error","invalid","Non-object section"));continue
        label=str(section.get("name","unnamed"))
        bars=section.get("bars")
        if bars is None or isinstance(bars,bool) or not isinstance(bars,int) or bars<=0:
            findings.append(Finding("GRID_BARS","unverified","unverified",label+": missing/invalid bars"))
        elif bars not in (16,32):
            findings.append(Finding("GRID_BARS","review","profile_divergence",label+": 4C suggests 16/32 bars"))
        if section.get("kick_removed") is True:
            findings.append(Finding("KICK_BREAK","review","conditional_conflict",label+": intentional breakdown may justify kick removal"))
        if section.get("chaos") and section.get("type") not in ("build","drop","final_build","final_drop"):
            findings.append(Finding("CHAOS_CONTEXT","review","conditional_conflict",label+": track-specific rationale needed"))
    drops=track.get("drops")
    if isinstance(drops,list) and len(drops)>=2 and isinstance(drops[0],dict) and isinstance(drops[-1],dict):
        first,last=drops[0].get("intended_energy"),drops[-1].get("intended_energy")
        if isinstance(first,(int,float)) and isinstance(last,(int,float)) and last<=first:
            findings.append(Finding("MULTI_DROP_CONTRAST","review","conditional_conflict","Contrast may be emotional or structural instead of loudness"))
    end=track.get("ending")
    if end is None:
        findings.append(Finding("END_CONTROL","review","unverified","Ending not specified"))
    elif not isinstance(end,dict):
        findings.append(Finding("END_CONTROL","error","invalid","Ending must be an object"))
    elif end.get("type")!="controlled_hard_stop":
        findings.append(Finding("END_CONTROL","review","profile_divergence","4C hard stop is a preference, not global authority"))
    else:
        findings.append(Finding("END_CONTROL","review","declared_not_audio_verified","Design claim, not measured audio"))
    if reference is not None:
        a,b=track.get("dna") or {},reference.get("dna") or {}
        covered=[k for k in DNA if a.get(k) is not None and b.get(k) is not None]
        same=[k for k in covered if a[k]==b[k]]
        result="insufficient_comparison" if len(covered)<3 else "candidate_similarity" if len(same)>=3 else "no_rule_hit"
        findings.append(Finding("ANTI_CLONE","review",result,"Declared DNA matches: "+", ".join(same)+"; audio not required"))
    return {"system_id":"666TDI-001","component":"4C_ADDITIVE_CANDIDATE","profile":profile,
        "source_status":"HISTORICAL_USER_PROVIDED_NOT_PROMOTED","input_mode":"DECLARED_TRACK_STRUCTURE_ONLY",
        "findings":[asdict(f) for f in findings],"writes":False,"audio_verified":False,
        "audio_analysis_required":False,"global_rules_changed":False}
