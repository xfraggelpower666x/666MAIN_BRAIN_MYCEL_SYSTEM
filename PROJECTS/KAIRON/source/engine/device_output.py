"""666TDI R1.3: creator-evidence-scoped Suno device output adapter.

Only translates creator-supplied content; not a composer, Suno control or provider API.
R0.9–R1.2 musical intelligence stays device-independent and unchanged.
"""
from __future__ import annotations
import re
from . import semantic_guard

SCHEMA="666TDI_DEVICE_OUTPUT_R13_V1"
SYSTEM_ID="666TDI-001"
BUDGETS={"title":80,"extended":1000,"style":1000,"lyrics":5000}
ROUTES={"IPHONE_CUSTOM_NO_MAIN","IPHONE_CUSTOM_WITH_MAIN","PC_BROWSER"}
PROVENANCE={
 "type":"LYVRA_CREATOR_REPORTED_WORKFLOW_REFERENCE_NOT_PROVIDER_LIVE_VERIFIED",
 "branch":"lyvra",
 "reference":"LYVRA_NATIVE_RUNTIME/current/music/TRACK_DESIGN_IPHONE_CUSTOM_THREE_ROUTES_20261029.md",
 "scope":"OUTPUT_SURFACE_ONLY_NO_FOREIGN_MUSIC_AUTHORITY",
}
def utf16_length(value):
 if not isinstance(value,str): raise ValueError("INVALID_OUTPUT_TEXT")
 return len(value.encode("utf-16-le"))//2

def _section(label,value):
 if not isinstance(value,str): raise ValueError("INVALID_CREATOR_FIELD:"+label)
 return label+": "+value if value.strip() else ""

def _join(*parts):
 return "\n".join(p for p in parts if p)

def _field(value,budget):
 count=utf16_length(value)
 return {"text":value,"utf16_units":count,"reference_budget":budget,
         "within_reference_budget":count<=budget,
         "copy_ready":bool(value.strip()) and count<=budget,
         "status":"OVER_REFERENCE_BUDGET_CREATOR_REVIEW" if count>budget
                  else "CREATOR_SOURCE_EMPTY" if not value.strip()
                  else "WITHIN_CREATOR_REPORTED_REFERENCE_BUDGET"}

def translate(intent, device, route_context=None):
 """Create exact counted copy payloads from creator text without silent truncation."""
 if not isinstance(intent,dict): raise ValueError("INVALID_INTENT")
 if device not in ("IPHONE_SUNO_APP","PC_SUNO_BROWSER"): raise ValueError("DEVICE_PREFLIGHT_REQUIRED")
 if route_context is None: route_context={}
 if not isinstance(route_context,dict): raise ValueError("INVALID_ROUTE_CONTEXT")
 main = route_context.get("iphone_main_input",False)
 visible = route_context.get("pc_duration_slider_visible",None)
 if not isinstance(main,bool): raise ValueError("INVALID_MAIN_INPUT_CHOICE")
 if visible is not None and not isinstance(visible,bool): raise ValueError("INVALID_SLIDER_VISIBILITY")
 main_text=route_context.get("main_input_text","")
 if not isinstance(main_text,str) or len(main_text)>12000: raise ValueError("INVALID_MAIN_INPUT_TEXT")
 duration=route_context.get("pc_selected_duration","")
 if not isinstance(duration,str): raise ValueError("INVALID_DURATION_TARGET")
 if device=="IPHONE_SUNO_APP":
  if visible is not None or duration:
   raise ValueError("PC_DURATION_CONTROL_NOT_ALLOWED_ON_IPHONE")
  route="IPHONE_CUSTOM_WITH_MAIN" if main else "IPHONE_CUSTOM_NO_MAIN"
  if not main and main_text.strip(): raise ValueError("MAIN_INPUT_NOT_ENABLED")
 else:
  if main or main_text.strip(): raise ValueError("MAIN_INPUT_NOT_AVAILABLE_ON_PC_REFERENCE")
  route="PC_BROWSER"
  if duration and visible is not True: raise ValueError("PC_DURATION_NOT_CONFIRMED_VISIBLE")
  if duration and not re.fullmatch(r"[0-9]{1,2}:[0-5][0-9]",duration):
   raise ValueError("INVALID_DURATION_TARGET")
 def value(key):
  x=intent.get(key,"")
  if x is None:return ""
  if not isinstance(x,str):raise ValueError("INVALID_CREATOR_FIELD:"+key)
  return x
 title=value("title")
 # Source-faithful translation: labels only; no invented motifs/lyrics/musical instructions.
 extended=_join(
  _section("Intent",value("story")),
  _section("Structure",value("structure")),
  _section("Energy",value("energy")),
  _section("Psychoacoustics",value("psychoacoustics")),
  _section("Voice role",value("voice")),
  _section("Ending",value("ending")),
  _section("Avoid",value("avoid")),
 )
 style=_join(
  value("genre"),
  _section("LOW",value("motor")),
  _section("MID",value("mid")),
  _section("HIGH",value("high")),
  _section("Atmosphere",value("atmosphere")),
 )
 lyrics=value("lyrics")
 fields={
  "title":_field(title,BUDGETS["title"]),
  "extended":_field(extended,BUDGETS["extended"]),
  "style":_field(style,BUDGETS["style"]),
  "lyrics":_field(lyrics,BUDGETS["lyrics"]),
 }
 main_output=None
 if route=="IPHONE_CUSTOM_WITH_MAIN":
  main_output={"text":main_text,"utf16_units":utf16_length(main_text),
               "status":"CREATOR_EXPLICIT_EMPTY_PRESERVED" if not main_text else "CREATOR_SUPPLIED_UNVERIFIED_FIELD_LIMIT",
               "copy_ready":bool(main_text),
               "reference_budget":None}
 guidance={
  "IPHONE_CUSTOM_NO_MAIN":[
   "Do not assume a Duration slider or a separate Exclude Styles field.",
   "Use only the creator's actual Custom input fields; no Main Input is introduced.",
   "Duration and endings are musical design considerations, not promised render outcomes."],
  "IPHONE_CUSTOM_WITH_MAIN":[
   "Main Input is optional and only creator-authored; an explicitly empty Main stays empty.",
   "No separate Duration slider or Exclude Styles controls are assumed.",
   "Main storyboard has no provider-verified character limit here."],
  "PC_BROWSER":[
   "Main Input is not available in the referenced creator PC workflow.",
   "Use Duration slider only if the creator explicitly confirms that it is visible.",
   "Do not import iPhone no-slider compensation into the PC output."]
 }[route]
 return {
  "schema":SCHEMA,"system_id":SYSTEM_ID,
  "route":route,"device":device,"provenance":PROVENANCE,
  "source_integrity":"CREATOR_TEXT_ONLY_NO_AUTOMATIC_TRACK_REWRITE",
  "fields":fields,"main_input":main_output,
  "semantic_reinforcement_audit":semantic_guard.review(fields,intent),
  "pc_duration_control":{"visibility":"CREATOR_CONFIRMED_VISIBLE" if visible is True
          else "CREATOR_CONFIRMED_NOT_VISIBLE" if visible is False else "NOT_CONFIRMED",
          "selected_duration":duration if visible is True else "",
          "not_a_render_guarantee":True},
  "guidance":guidance,
  "field_order":["title","extended","style","lyrics"],
  "copy_budget_claim":"CREATOR_REPORTED_REFERENCE_NOT_LIVE_PROVIDER_VERIFIED",
  "requires_creator_review":True,
  "all_nonempty_fields_within_reference_budget":all(v["within_reference_budget"] for v in fields.values()),
  "renderer_executed":False,"suno_connected":False,"global_learning":False,"read_only":True,
  "limitations":["NO_AUTOMATIC_PROMPT_CREATION_FROM_CAUSAL_HYPOTHESES",
                 "NO_PROVIDER_VERIFIED_UI_FIELDS_OR_LIMITS",
                 "NO_AUTOMATIC_FIELD_TRUNCATION",
                 "NO_REAL_RENDER_OR_AUDIO_MEASUREMENT"]
 }
