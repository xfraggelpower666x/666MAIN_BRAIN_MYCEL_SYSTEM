"""666TDI R1.4: creator-reviewed, track-local feedback ledger.

Evidence is creator-reported until separately verified. No causal proof, Suno
execution, automatic global promotion, or foreign-system memory writes.
"""
from __future__ import annotations
import hashlib,json,os,re,tempfile
from threading import RLock
from datetime import datetime,timezone
from pathlib import Path

SYSTEM_ID="666TDI-001"
SCHEMA="666TDI_CREATOR_EVIDENCE_R14_V1"
CATEGORY={"MOTOR","VOICE","ARRANGEMENT","PRESSURE","DYNAMICS","ATMOSPHERE","ENDING","OTHER"}
RATING={"SUCCESS","MIXED","UNSUCCESSFUL"}
MAX_RECORDS=5000
_LEDGER_WRITE_LOCK=RLock()

def _canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _hash(value):return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()
def _text(value,name,limit,required=True):
 if not isinstance(value,str):raise ValueError("INVALID_"+name)
 value=value.strip()
 if (required and not value) or len(value)>limit:raise ValueError("INVALID_"+name)
 return value
def _track(value):
 value=_text(value,"TRACK_ID",96)
 if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}",value) or value.startswith("."):
  raise ValueError("INVALID_TRACK_ID")
 return value
def _validate_input(payload):
 if not isinstance(payload,dict):raise ValueError("INVALID_FEEDBACK_INPUT")
 if payload.get("creator_confirmed") is not True:raise ValueError("CREATOR_CONFIRMATION_REQUIRED")
 track_id=_track(payload.get("track_id"))
 decision=_text(payload.get("decision_id"),"DECISION_ID",160)
 category=payload.get("category");rating=payload.get("rating")
 if not isinstance(category,str) or not isinstance(rating,str) or category not in CATEGORY or rating not in RATING:raise ValueError("INVALID_CATEGORY_OR_RATING")
 expected=_text(payload.get("intent_summary"),"INTENT_SUMMARY",1600)
 outcome=_text(payload.get("observed_outcome"),"OBSERVED_OUTCOME",1600)
 review=_text(payload.get("creator_note",""),"CREATOR_NOTE",1600,False)
 artifact=_text(payload.get("artifact_sha256",""),"ARTIFACT_SHA256",64,False)
 if artifact and not re.fullmatch(r"[a-fA-F0-9]{64}",artifact):raise ValueError("INVALID_ARTIFACT_SHA256")
 surface=_text(payload.get("device_route","UNKNOWN"),"DEVICE_ROUTE",64)
 if surface not in ("UNKNOWN","IPHONE_CUSTOM_NO_MAIN","IPHONE_CUSTOM_WITH_MAIN","PC_BROWSER"):raise ValueError("INVALID_DEVICE_ROUTE")
 return {"system_id":SYSTEM_ID,"schema":SCHEMA,"track_id":track_id,"decision_id":decision,
         "category":category,"rating":rating,"intent_summary":expected,"observed_outcome":outcome,
         "creator_note":review,"artifact_sha256":artifact.lower(),"device_route":surface,
         "evidence_type":"CREATOR_REPORTED_OUTCOME","creator_confirmed":True,
         "audio_measured_by_tdi":False,"causal_proof":False,"global_rule":False}

def prepare(payload,*,now=None):
 item=_validate_input(payload)
 moment=now if now is not None else datetime.now(timezone.utc).isoformat()
 item["created_utc"]=_text(moment,"TIMESTAMP",64)
 item["content_hash"]=_hash({k:v for k,v in item.items() if k not in ("content_hash","id")})
 item["id"]="tdi-feedback-"+item["content_hash"][:24]
 return item

def _path(root,track_id):
 return Path(root).resolve()/"creator_evidence"/(_track(track_id)+".jsonl")

def _load(root,track_id):
 file=_path(root,track_id)
 if not file.exists():return []
 rows=[]
 with file.open("r",encoding="utf-8") as stream:
  for line in stream:
   if not line.strip():raise ValueError("EVIDENCE_EMPTY_LINE")
   try:value=json.loads(line)
   except json.JSONDecodeError as err:raise ValueError("EVIDENCE_CORRUPT_JSON") from err
   if not isinstance(value,dict) or value.get("system_id")!=SYSTEM_ID or value.get("schema")!=SCHEMA or value.get("track_id")!=track_id:
    raise ValueError("EVIDENCE_SCOPE_MISMATCH")
   digest=_hash({k:v for k,v in value.items() if k not in ("content_hash","id")})
   if digest!=value.get("content_hash") or value.get("id")!="tdi-feedback-"+digest[:24]:
    raise ValueError("EVIDENCE_HASH_MISMATCH")
   rows.append(value)
   if len(rows)>MAX_RECORDS:raise ValueError("EVIDENCE_LIMIT_EXCEEDED")
 ids=[x["id"] for x in rows]
 if len(ids)!=len(set(ids)):raise ValueError("EVIDENCE_DUPLICATE_ID")
 return rows

def _record_unlocked(root,payload):
 """Explicit creator-confirmed write, local atomic snapshot, no side-effect during assess."""
 item=prepare(payload)
 file=_path(root,item["track_id"]);file.parent.mkdir(parents=True,exist_ok=True)
 rows=_load(root,item["track_id"])
 if any(x["id"]==item["id"] for x in rows):
  return {"status":"ALREADY_RECORDED","id":item["id"],"track_id":item["track_id"]}
 if len(rows)>=MAX_RECORDS:raise ValueError("EVIDENCE_LIMIT_EXCEEDED")
 fd,tmp=tempfile.mkstemp(dir=file.parent,prefix=".evidence-")
 try:
  with os.fdopen(fd,"w",encoding="utf-8") as out:
   for value in rows+[item]:out.write(_canonical(value)+"\n")
   out.flush();os.fsync(out.fileno())
  os.replace(tmp,file)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
 return {"status":"TRACK_LOCAL_CREATOR_EVIDENCE_RECORDED","id":item["id"],"track_id":item["track_id"],
         "global_rule":False,"causal_proof":False}

def record(root,payload):
 """Serialize local writes within the server process. The read-only assess stays independent."""
 with _LEDGER_WRITE_LOCK:
  return _record_unlocked(root,payload)

def assess(root,track_id):
 track_id=_track(track_id);rows=_load(root,track_id);groups={}
 for value in rows:groups.setdefault((value["category"],value["decision_id"]),[]).append(value)
 relations=[]
 for (category,decision),values in sorted(groups.items()):
  counts={rating:sum(x["rating"]==rating for x in values) for rating in sorted(RATING)}
  contradictory="SUCCESS" in {v["rating"] for v in values} and "UNSUCCESSFUL" in {v["rating"] for v in values}
  status="CONTRADICTORY_OUTCOMES_REVIEW_REQUIRED" if contradictory else "SINGLE_OUTCOME_CANDIDATE" if len(values)<2 else "REPEATED_TRACK_LOCAL_OBSERVATION_NOT_GENERALIZED"
  relations.append({"category":category,"decision_id":decision,"observations":len(values),
   "distinct_tracks":len({v["track_id"] for v in values}),"counts":counts,"contradiction":contradictory,
   "status":status,"evidence_ids":[v["id"] for v in values],
   "claim":"Creator-rated track-local correlation; not independent or controlled causal proof",
   "global_rule":False,"automatic_promotion":False})
 return {"schema":"666TDI_CREATOR_LEARNING_REPORT_R14_V1","system_id":SYSTEM_ID,
  "track_id":track_id,"observations":len(rows),"relations":relations,
  "has_contradictions":any(x["contradiction"] for x in relations),
  "status":"TRACK_LOCAL_REVIEW_REQUIRED" if relations else "NO_CREATOR_EVIDENCE",
  "creator_records":[{"id":x["id"],"category":x["category"],"decision_id":x["decision_id"],
    "rating":x["rating"],"observed_outcome":x["observed_outcome"],
    "intent_summary":x["intent_summary"],"created_utc":x["created_utc"],
    "artifact_sha256":x["artifact_sha256"]} for x in rows],
  "global_promotion":False,"causal_proof":False,"read_only":True,
  "limitations":["CREATOR_FEEDBACK_NOT_VERIFIED_AUDIO","NO_CROSS_TRACK_GENERALIZATION",
   "NO_AUTOMATIC_GLOBAL_RULE","CONTRADICTIONS_PRESERVED"]}
