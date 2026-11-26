"""R1.5: track-local semantic reinforcement candidates and output survival.
No autonomous rewriting, audio proof, fixed emoji quota or foreign authority.
"""
import re
from . import semantic_intelligence as semantic

# Contextual examples, not a mandatory dictionary or an intensity scale.
RELATIONS=(
 ("fire","🔥","spectral heat / energy"),("feuer","🔥","spectral heat / energy"),
 ("spiral","🌀","rotating upper-field motion"),("rotation","🌀","rotating upper-field motion"),
 ("electric energy","⚡","transient signal exchange"),("explosion","💥","release contrast"),
 ("final stop","🛑🔚","terminal closure"),("complete silence","🔇","terminal silence"),
)
FIELDS={"extended":("story","structure","energy","psychoacoustics","voice","ending"),
        "style":("genre","motor","mid","high","atmosphere"),"lyrics":("lyrics",)}
def assess(intent):
    candidates=[]
    for target, fields in FIELDS.items():
        for field in fields:
            value=intent.get(field,"")
            if not isinstance(value,str): continue
            for clause in semantic._clauses(value):
                for term,symbol,job in RELATIONS:
                    if semantic._contains_phrase(clause,term) and not semantic._negated(clause,term):
                        candidates.append({"field":target,"source_field":field,"anchor":term,
                           "clause":clause,"symbol":symbol,"function":job,
                           "status":"CONTEXT_REVIEW","retain_words":True})
    genre=str(intent.get("genre",""))
    active=semantic.assess(intent)
    functions=[f["id"] for f in active["functions"] if f["status"]=="SUPPORTED"]
    return {"system_id":"666TDI-001","schema":"666TDI_R15_V1","candidates":candidates,
       "genre_roles":[x.strip() for x in re.split(r"[,;|]",genre) if x.strip()],
       "genre_guidance":"Prefer two leading psychedelic roles, dark preference; third contextual; exclude Psycore; review ambiguous labels.",
       "tempo_preference":[142,150],"above_range":"CONTEXTUAL",
       "bpm":intent.get("bpm"),"hardness_from_bpm":False,
       "chaos":{"candidate":"LOW anchor; reactive MID/HIGH events; micro contrast; macro direction",
                "functions":functions,"protect_voice":True,"melody_not_dominant_by_default":True},
       "lyric_relations":lyric_relations(intent.get("lyrics","") or ""),
       "read_only":True,"global_promotion":False,"audio_verified":False}
def lyric_relations(text):
    """Recognize explicit roles without treating every parenthesis as an echo."""
    rows=[]
    terminal=False
    for i,line in enumerate(text.splitlines(),1):
        s=line.strip()
        if not s: continue
        if s.startswith("[") and s.endswith("]"):
            command=s[1:-1].casefold()
            if "all vocals end here" in command: terminal=True
            rows.append({"line":i,"role":"COMMAND","text":s,"after_vocal_end":terminal})
        elif s.startswith("(") and s.endswith(")"):
            rows.append({"line":i,"role":"RESPONSE_CANDIDATE","text":s,"after_vocal_end":terminal})
        else:
            rows.append({"line":i,"role":"LYRIC","text":s,"after_vocal_end":terminal})
    return {"rows":rows,"vocal_end_present":terminal,
            "post_end_vocal_candidates":[x["line"] for x in rows if x["after_vocal_end"] and x["role"]!="COMMAND"],
            "review_required":any(x["after_vocal_end"] and x["role"]!="COMMAND" for x in rows)}

def apply_reviewed_bindings(text, bindings, budget):
    """Apply only exact, explicitly approved span bindings, never truncate."""
    if not isinstance(text,str) or not isinstance(bindings,list) or type(budget) is not int or budget<0:
        raise ValueError("INVALID_BINDING_INPUT")
    out=text
    positions=set()
    for b in sorted(bindings,key=lambda b:b["end"],reverse=True):
        start,end=b["start"],b["end"]
        anchor,symbol=b["anchor"],b["symbol"]
        if b.get("creator_approved") is not True or type(start) is not int or type(end) is not int:
            raise ValueError("BINDING_APPROVAL_REQUIRED")
        if not isinstance(anchor,str) or not anchor or not isinstance(symbol,str) or not symbol or not 0<=start<end<=len(text):
            raise ValueError("INVALID_BINDING_SPAN")
        if text[start:end]!=anchor or end in positions:
            raise ValueError("STALE_OR_DUPLICATE_BINDING")
        # Only documented candidate symbols; repetition is contextual and approved.
        allowed={s for _,s,_ in RELATIONS}
        if not any(symbol==s*n for s in allowed for n in range(1,9)):
            raise ValueError("UNSUPPORTED_SYMBOL")
        positions.add(end)
        if not text[end:].lstrip().startswith(symbol):
            out=out[:end]+" "+symbol+out[end:]
    if len(out.encode("utf-16-le"))//2>budget:
        raise ValueError("OVER_REFERENCE_BUDGET_NO_TRUNCATION")
    return out

def audit(fields, analysis):
    # Audit candidate anchors only; never silently alter creator text or block an unrelated track.
    rows=[]
    for c in analysis["candidates"]:
        value=fields.get(c["field"],{}).get("text","")
        matches=[line for line in value.splitlines() if semantic._contains_phrase(line,c["anchor"])]
        rows.append({**c,"anchor_survives":bool(matches),
            "symbol_present_on_anchor_line":any(c["symbol"] in line for line in matches),
            "review_required":not any(c["symbol"] in line for line in matches)})
    return {"checks":rows,"status":"CREATOR_REVIEW" if any(r["review_required"] for r in rows) else "CANDIDATE_CHECK_COMPLETE",
       "no_automatic_rewrite":True,"no_render_guarantee":True}
