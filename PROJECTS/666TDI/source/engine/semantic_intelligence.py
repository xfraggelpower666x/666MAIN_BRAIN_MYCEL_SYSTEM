"""666TDI R0.9: context-aware musical function interpretation.

Transparent, evidence-bound heuristics. This module interprets creator intent;
it does not claim human-level understanding, audio perception or causality.
"""
from __future__ import annotations
import re

SCHEMA = "666TDI_SEMANTIC_INTELLIGENCE_R09_V1"
SYSTEM_ID = "666TDI-001"

# Each concept maps language to a musical job, not to a fixed prompt preset.
FUNCTIONS = {
    "FORWARD_MOTION": {
        "terms": ("forward motion", "forward", "marching", "relentless", "rolling groove",
                  "rolling", "drive", "driving", "straight motor", "vorwärts", "marschierend",
                  "treibend", "unaufhaltsam"),
        "job": "Keep the track moving continuously without requiring constant density.",
        "use": "Protects the kinetic carrier and DJ-mixable forward motion.",
        "constraint": "Do not create movement by destabilizing the low-end pulse."
    },
    "LOW_ANCHOR": {
        "terms": ("stable low", "stable sub", "mono sub", "dry kick", "straight kick",
                  "psy bass", "psybass", "low anchor", "stabiler sub", "trockene kick",
                  "kick bass", "kick-bass"),
        "job": "Provide a stable low-frequency timing and weight reference.",
        "use": "Keeps the physical motor legible while upper layers move.",
        "constraint": "Avoid uncontrolled low-end swing, phase spread or masking."
    },
    "VOICE_CLARITY": {
        "terms": ("clear vocal", "intelligible lyrics", "understandable lyrics",
                  "dry centered voice", "foreground voice", "clear words",
                  "verständliche vocals", "verständlicher gesang", "klare stimme",
                  "vocal clarity", "voice in front"),
        "job": "Keep the intended words perceptually intelligible and foregrounded.",
        "use": "Preserves narrative meaning rather than treating vocals as texture only.",
        "constraint": "Competing midrange layers may need carving, ducking or temporal separation."
    },
    "VOCAL_PRESENCE": {
        "terms": ("vocal", "vocals", "voice", "spoken", "whisper", "lyrics",
                  "gesang", "stimme", "gesprochen", "flüstern"),
        "job": "Establish a human or character-bearing voice role.",
        "use": "Gives the arrangement a semantic carrier when the track needs one.",
        "constraint": "Presence alone does not imply dominance, intelligibility or multiple voices."
    },
    "DENSE_LAYERS": {
        "terms": ("dense layers", "layered", "multi-layer", "stacked", "dense acid",
                  "busy midrange", "thick arrangement", "dichte layer", "geschichtet",
                  "dichte acid"),
        "job": "Increase arrangement density through simultaneous sound layers.",
        "use": "Adds pressure, detail and spectral activity when the arrangement has room.",
        "constraint": "Check voice intelligibility and transient separation."
    },
    "SPATIAL_MOTION": {
        "terms": ("spatial motion", "stereo orbit", "orbit", "wide movement",
                  "spatial rotation", "räumliche bewegung", "stereo bewegung",
                  "spatial", "pan movement"),
        "job": "Create perceived movement in the spatial field.",
        "use": "Adds motion without changing the low-end timing foundation.",
        "constraint": "Keep sub and kick stable; spatial width is not a substitute for groove."
    },
    "TENSION": {
        "terms": ("build tension", "tension", "suspense", "pressure rise",
                  "rising pressure", "build", "steigerung", "spannung", "druckaufbau"),
        "job": "Create expectation through controlled accumulation or withholding.",
        "use": "Makes a later release feel earned rather than arbitrary.",
        "constraint": "A promised tension arc needs a release, transformation or deliberate unresolved ending."
    },
    "RELEASE": {
        "terms": ("release", "drop", "impact", "explosive return", "final thrust",
                  "release", "entladung", "drop", "einschlag", "rückkehr"),
        "job": "Discharge accumulated expectation through a defined musical event.",
        "use": "Turns preparation into a perceptible payoff.",
        "constraint": "Impact needs contrast or a meaningful change in the preceding state."
    },
    "REPETITION": {
        "terms": ("loop", "repetition", "repeat", "refrain", "mantra", "recurring hook",
                  "wiederholung", "wiederkehr", "refrain"),
        "job": "Use recurrence to establish recognition, ritual or motor stability.",
        "use": "Creates memory and hypnotic continuity.",
        "constraint": "If evolution is requested, recurrence should transform rather than merely copy."
    },
    "VARIATION": {
        "terms": ("variation", "evolve", "evolving", "mutate", "transformation",
                  "change over time", "develop", "entwicklung", "wandlung", "verwandlung"),
        "job": "Change a returning element while preserving its identity.",
        "use": "Creates progression and prevents static repetition.",
        "constraint": "Variation should retain a recognizable anchor or intentional contrast."
    },
    "DYNAMIC_CONTRAST": {
        "terms": ("deep break", "vacuum", "dropout", "silence", "breakdown",
                  "contrast", "leeraum", "pause", "break", "entlastung"),
        "job": "Create a temporary reduction or absence that changes perceived pressure.",
        "use": "Makes re-entry and impact more significant.",
        "constraint": "A break must be placed in time; it need not destroy the continuous motor everywhere."
    },
    "FINALITY": {
        "terms": ("hard stop", "final hit", "terminal ending", "clear ending",
                  "end cleanly", "final landing", "harter stopp", "klares ende",
                  "schlussakkord", "terminal"),
        "job": "Make the final state unmistakable and prevent unintended continuation.",
        "use": "Provides a deliberate endpoint rather than an arbitrary fade or loop.",
        "constraint": "A fake ending and reactivation require a separate later terminal landing."
    },
    "BASS_SWING": {
        "terms": ("bouncy bass", "swing bass", "swung bass", "shuffle bass",
                  "bounce bass", "hüpfender bass", "swingender bass"),
        "job": "Introduce elastic or swung low-frequency movement.",
        "use": "Can create looseness when that is the intended motor character.",
        "constraint": "May undermine a straight, tightly locked psy motor."
    },
    "STATIC_REPETITION": {
        "terms": ("static loop", "unchanging loop", "identical repetition",
                  "mechanical repetition", "statischer loop", "mechanische wiederholung"),
        "job": "Repeat an element without meaningful transformation.",
        "use": "Can serve a deliberately fixed hypnotic passage.",
        "constraint": "Conflicts with an explicit demand for evolution or changing return."
    },
    "LONG_SILENCE": {
        "terms": ("long silence", "extended silence", "long empty break",
                  "extended empty section", "lange stille", "langer leerraum"),
        "job": "Remove most or all musical activity for an extended interval.",
        "use": "Can create a dramatic reset when the arrangement calls for it.",
        "constraint": "Can interrupt an explicitly continuous motor if not sectionally contained."
    }
}

NEGATORS = ("not", "no", "never", "without", "avoid", "avoidance",
            "nicht", "kein", "keine", "keinen", "keinem", "ohne",
            "vermeide", "niemals", "nie", "nicht mehr")
CONTRAST_WORDS = ("but", "however", "instead", "rather", "yet",
                  "sondern", "aber", "jedoch", "stattdessen", "hingegen")
RESOLUTION_CUES = ("alternating", "separate sections", "call and response",
                   "duck", "carve", "sidechain", "sparse verse", "break then",
                   "then return", "sectional", "abwechselnd", "getrennte parts",
                   "freiraum", "ausdünnen", "danach zurück")

CONFLICTS = (
    ("VOICE_CLARITY", "DENSE_LAYERS", "Simultaneous dense midrange may mask words."),
    ("LOW_ANCHOR", "BASS_SWING", "A swung or bouncy bass may weaken a straight low-end anchor."),
    ("FORWARD_MOTION", "LONG_SILENCE", "An extended empty section may interrupt continuous forward motion."),
    ("REPETITION", "VARIATION", "Recurrence and transformation need a clear balance."),
    ("STATIC_REPETITION", "VARIATION", "An unchanged loop contradicts a request for meaningful evolution."),
    ("VOCAL_PRESENCE", "DENSE_LAYERS", "Voice presence can compete with simultaneous dense layers.")
)

FIELD_ORDER = ("title", "genre", "story", "motor", "mid", "high", "voice",
               "lyrics", "structure", "psychoacoustics", "energy", "atmosphere",
               "ending", "avoid")

def _clauses(value):
    # Keep clause boundaries explicit so negation does not leak across sentences.
    parts = re.split(r"[.!?;\\n]+|\\b(?:but|however|instead|rather|yet|sondern|aber|jedoch|stattdessen|hingegen)\\b",
                     str(value), flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]

def _contains_phrase(text, phrase):
    return re.search(r"(?<!\\w)" + re.escape(phrase) + r"(?!\\w)", text, flags=re.IGNORECASE) is not None

def _negated(clause, phrase):
    pos = clause.casefold().find(phrase.casefold())
    if pos < 0:
        return False
    prefix = clause[:pos].casefold()
    words = re.findall(r"[\\wäöüß]+", prefix)[-5:]
    return any(n in words for n in NEGATORS)

def _evidence_for(track):
    found = []
    for field in FIELD_ORDER:
        raw = track.get(field)
        if not isinstance(raw, str) or not raw.strip():
            continue
        for clause in _clauses(raw):
            for function_id, spec in FUNCTIONS.items():
                for phrase in spec["terms"]:
                    if not _contains_phrase(clause, phrase):
                        continue
                    negated = field == "avoid" or _negated(clause, phrase)
                    found.append({
                        "function": function_id,
                        "field": field,
                        "phrase": phrase,
                        "clause": clause,
                        "polarity": "CONSTRAINT" if negated else "SUPPORT",
                        "source": "EXPLICIT_AVOID_FIELD" if field == "avoid" else "CURRENT_TRACK_FIELD",
                        "scope": "TRACK_LOCAL"
                    })
    # Deterministic deduplication; keep separate field provenance.
    unique = {}
    for item in found:
        key = (item["function"], item["field"], item["phrase"], item["polarity"], item["clause"])
        unique[key] = item
    return list(unique.values())

def assess(track):
    """Return function-level evidence, counterrelations and reasons without mutation."""
    if not isinstance(track, dict):
        raise ValueError("TRACK_INTENT_MUST_BE_OBJECT")
    track_id = track.get("track_id")
    evidence = _evidence_for(track)
    grouped = {}
    for item in evidence:
        grouped.setdefault(item["function"], {"support": [], "constraints": []})
        key = "support" if item["polarity"] == "SUPPORT" else "constraints"
        grouped[item["function"]][key].append(item)

    functions = []
    for function_id, spec in FUNCTIONS.items():
        group = grouped.get(function_id)
        if not group:
            continue
        status = ("SUPPORTED_AND_CONSTRAINED" if group["support"] and group["constraints"]
                  else "SUPPORTED" if group["support"] else "EXPLICITLY_CONSTRAINED")
        functions.append({
            "id": function_id,
            "status": status,
            "support_evidence": group["support"],
            "constraint_evidence": group["constraints"],
            "musical_job": spec["job"],
            "why_it_matters": spec["use"],
            "design_guard": spec["constraint"],
            "confidence": "RULE_SUPPORTED_NOT_AUDIO_VERIFIED"
        })

    active = {x["id"] for x in functions if x["status"] in ("SUPPORTED", "SUPPORTED_AND_CONSTRAINED")}
    constraints = {x["id"] for x in functions if x["status"] in ("EXPLICITLY_CONSTRAINED", "SUPPORTED_AND_CONSTRAINED")}
    resolution_text = " ".join(str(track.get(k, "")) for k in ("structure", "psychoacoustics", "story")).casefold()
    has_resolution = any(cue in resolution_text for cue in RESOLUTION_CUES)
    collisions = []
    for left, right, reason in CONFLICTS:
        if left not in active or right not in active:
            continue
        resolved = has_resolution
        collisions.append({
            "functions": [left, right],
            "status": "SEQUENCING_OR_ARRANGEMENT_MAY_RESOLVE" if resolved else "POTENTIAL_COLLISION_REQUIRES_REVIEW",
            "reason": reason,
            "resolution_evidence": [cue for cue in RESOLUTION_CUES if cue in resolution_text],
            "not_a_proven_audio_defect": True
        })

    decisions = []
    for item in functions:
        if item["status"] in ("SUPPORTED", "SUPPORTED_AND_CONSTRAINED"):
            decisions.append({
                "function": item["id"],
                "decision": "PRESERVE_FUNCTION_AND_DESIGN_AROUND_ITS_CONSTRAINTS",
                "reason": item["why_it_matters"],
                "implementation_guard": item["design_guard"]
            })

    return {
        "schema": SCHEMA,
        "system_id": SYSTEM_ID,
        "track_id": track_id,
        "status": "SEMANTIC_FUNCTIONS_INTERPRETED" if functions else "INSUFFICIENT_SEMANTIC_EVIDENCE",
        "method": "EXPLICIT_PHRASE_EVIDENCE_WITH_CLAUSE_LOCAL_NEGATION_AND_FUNCTION_RELATIONS",
        "functions": functions,
        "collisions": collisions,
        "decisions": decisions,
        "evidence_count": len(evidence),
        "limitations": [
            "RULE_BASED_INTERPRETATION_NOT_HUMAN_LEVEL_UNDERSTANDING",
            "NO_AUDIO_PERCEPTION_OR_MASKING_PROOF",
            "NO_RENDERER_EXECUTION_OR_QUALITY_SCORE",
            "AMBIGUOUS_LANGUAGE_REQUIRES_CREATOR_REVIEW",
            "ALL_FINDINGS_TRACK_LOCAL_NO_GLOBAL_LEARNING"
        ],
        "read_only": True,
        "global_promotion": False
    }
