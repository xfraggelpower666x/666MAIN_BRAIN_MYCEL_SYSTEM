"""666TDI R1.0 — Creative Causal Emergence Intelligence.
Deterministic, evidence-bound reasoning over R0.9 semantic findings.
No audio perception, objective causal proof, quality score or autonomous composition.
"""
from __future__ import annotations
from . import semantic_intelligence as semantic

SCHEMA = "666TDI_CREATIVE_CAUSAL_R10_V1"
SYSTEM_ID = "666TDI-001"

EMERGENCE_RULES = (
 {"id":"PRESSURE_RELEASE_WITH_MOTOR_ANCHOR","requires":("FORWARD_MOTION","DYNAMIC_CONTRAST"),"relation":"PRODUCTIVE_TENSION","effect":"A stable kinetic carrier can make a temporary reduction feel more dramatic without abandoning forward identity.","decision":"PRESERVE_MOTOR_IDENTITY_AND_LOCALIZE_CONTRAST","counterfactual":"Without the stable carrier, contrast may read as a full stop rather than controlled pressure modulation."},
 {"id":"STABLE_CORE_MOVING_FIELD","requires":("LOW_ANCHOR","SPATIAL_MOTION"),"relation":"COMPLEMENTARY_SUPPORT","effect":"A stable low-frequency reference can coexist with perceived movement in upper spatial layers.","decision":"PROTECT_LOW_ANCHOR_WHILE_MOVING_UPPER_FIELD","counterfactual":"If spatial motion reaches the low anchor, the intended stable reference may weaken."},
 {"id":"VOICE_LAYER_NEGOTIATION","requires":("VOICE_CLARITY","DENSE_LAYERS"),"relation":"PRODUCTIVE_TENSION","effect":"Voice intelligibility and dense midrange can create deliberate foreground/background tension when arranged with space or temporal separation.","decision":"PRESERVE_TENSION_AND_DESIGN_VOICE_WINDOWS","counterfactual":"If both remain continuously dominant in the same range, intelligibility may be reduced.","requires_arrangement_review":True},
 {"id":"TRANSFORMING_RECURRENCE","requires":("REPETITION","VARIATION"),"relation":"TRANSFORMATIVE_SUPPORT","effect":"A recurring motif can remain recognizable while changing context, timbre, density or emotional meaning.","decision":"RETURN_WITH_HISTORY_NOT_IDENTICAL_REPLAY","counterfactual":"Without a recognizable anchor, variation may lose identity; without transformation, recurrence may become static."},
 {"id":"EXPECTATION_PAYOFF","requires":("TENSION","RELEASE"),"relation":"CAUSAL_SEQUENCE_HYPOTHESIS","effect":"A release can feel earned when it answers a previously established expectation.","decision":"CONNECT_RELEASE_TO_PRECEDING_TENSION","counterfactual":"Without preparation, release may feel arbitrary; without payoff, tension may remain unresolved."},
 {"id":"VOICE_AS_NARRATIVE_ANCHOR","requires":("VOICE_CLARITY","VARIATION"),"relation":"IDENTITY_PRESERVING_TRANSFORMATION","effect":"A recognizable vocal identity can survive changes in delivery, placement or surrounding arrangement.","decision":"VARY_CONTEXT_WITHOUT_LOSING_VOCAL_MEANING","counterfactual":"If every return changes the vocal identity, narrative continuity may weaken."}
)
RELATION_RULES = (
 (("FORWARD_MOTION","LOW_ANCHOR"),"SUPPORTS","The low anchor provides a stable physical reference for continuous motion."),
 (("VOICE_CLARITY","DENSE_LAYERS"),"POTENTIAL_COLLISION","Dense simultaneous layers may compete with intelligible words; this is not automatically a defect."),
 (("LOW_ANCHOR","BASS_SWING"),"CONSTRAINS","A swung bass may conflict with an explicitly straight low-end motor."),
 (("REPETITION","VARIATION"),"TRANSFORMS","Recurrence and variation can form a recognizable evolving motif."),
 (("TENSION","RELEASE"),"SEQUENCES","Release can answer an established expectation."),
 (("LOW_ANCHOR","SPATIAL_MOTION"),"COMPLEMENTARY","Upper-field motion can contrast with a stable low-frequency center.")
)

def _active(result):
 return {x["id"]:x for x in result.get("functions",[]) if x.get("status") in ("SUPPORTED","SUPPORTED_AND_CONSTRAINED")}

def _evidence(function):
 return [{"field":x.get("field"),"phrase":x.get("phrase"),"clause":x.get("clause"),"polarity":x.get("polarity"),"source":x.get("source")} for x in function.get("support_evidence",[])]

def assess(track, *, semantic_report=None):
 if not isinstance(track,dict): raise ValueError("TRACK_INTENT_MUST_BE_OBJECT")
 sem=semantic.assess(track) if semantic_report is None else semantic_report
 if (not isinstance(sem,dict) or sem.get('schema')!=semantic.SCHEMA or
     sem.get('system_id')!=SYSTEM_ID or sem.get('track_id')!=track.get('track_id')):
  raise ValueError('SEMANTIC_SCOPE_MISMATCH')
 active=_active(sem)
 constrained={x["id"]:x for x in sem.get("functions",[]) if x.get("status") in ("EXPLICITLY_CONSTRAINED","SUPPORTED_AND_CONSTRAINED")}
 relations=[]
 for pair,kind,why in RELATION_RULES:
  if all(k in active for k in pair):
   relations.append({"functions":list(pair),"relation":kind,"rationale":why,"evidence":{k:_evidence(active[k]) for k in pair},"status":"RULE_DERIVED_TRACK_LOCAL_HYPOTHESIS","audio_verified":False})
 emergences=[]; decisions=[]
 for rule in EMERGENCE_RULES:
  req=rule["requires"]
  if not all(k in active for k in req): continue
  blocked=[k for k in req if k in constrained]
  item={"id":rule["id"],"functions":list(req),"relation":rule["relation"],"effect":rule["effect"],"counterfactual":rule["counterfactual"],"evidence":{k:_evidence(active[k]) for k in req},"constraints":blocked,"status":"CONSTRAINED_EMERGENCE_REQUIRES_CREATOR_REVIEW" if blocked else "CREATIVE_EMERGENCE_CANDIDATE","audio_verified":False}
  if rule.get("requires_arrangement_review"): item["arrangement_review_required"]=True
  emergences.append(item)
  decisions.append({"emergence":rule["id"],"recommendation":rule["decision"],"reason":rule["effect"],"preserve_creator_intent":True,"requires_creator_approval":True,"automatic_repair":False})
 collisions=[]
 for x in sem.get("collisions",[]):
  collisions.append({**x,"interpretation":"Potential functional tension; retain it when it serves the intended expression." if x.get("status")=="POTENTIAL_COLLISION_REQUIRES_REVIEW" else "Arrangement cues may create a resolution path; audio outcome remains unverified.","automatic_error":False})
 return {"schema":SCHEMA,"system_id":SYSTEM_ID,"track_id":track.get("track_id"),"status":"CREATIVE_RELATIONS_INTERPRETED" if active else "INSUFFICIENT_SEMANTIC_EVIDENCE","method":"R09_SEMANTIC_EVIDENCE_PLUS_EXPLICIT_FUNCTION_RELATION_AND_EMERGENCE_RULES","functions":[{"id":k,"status":v["status"],"evidence":_evidence(v)} for k,v in active.items()],"relations":relations,"emergences":emergences,"decisions":decisions,"collisions":collisions,"limitations":["DETERMINISTIC_RULE_BASED_REASONING_NOT_HUMAN_LEVEL_MUSICAL_UNDERSTANDING","NO_AUDIO_PERCEPTION_OR_CAUSAL_PROOF","NO_RENDERER_EXECUTION_OR_QUALITY_SCORE","CREATOR_REVIEW_REQUIRED_FOR_AMBIGUOUS_OR_CONSTRAINED_RELATIONS","TRACK_LOCAL_READ_ONLY_NO_GLOBAL_LEARNING"],"read_only":True,"global_promotion":False,"renderer_override":False}
