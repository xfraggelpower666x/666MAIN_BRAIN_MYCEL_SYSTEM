"""666TDI R1.2: Evidence-bounded pre-analysis of musical chapters and layer interplay.

Consumes existing R0.9/R1.0 findings. No independent composer, preset controller,
audio measurements, renderer execution, or invented story-specific events.
"""
from __future__ import annotations

SCHEMA = "666TDI_PREANALYSIS_R12_V1"
PHASES = (
    ("OPENING", "Origin / Introduction", 0.30, "Introduce an identifiable musical anchor without claiming a fixed genre formula."),
    ("MOTION", "Establish Movement", 0.65, "Establish the requested kinetic carrier and listener orientation."),
    ("DEVELOPMENT", "Motif Development", 0.78, "Develop recognizable elements and introduce variation if explicitly supported."),
    ("TENSION", "Creative Tension", 0.88, "Present an unresolved question or pressure transition when artistically intended."),
    ("CONTRAST", "Contrast / Space", 0.37, "Create contrast without automatically treating reduced density as a broken motor."),
    ("RETURN", "Reactivation", 0.94, "Bring selected anchors back with meaningful change."),
    ("CONVERGENCE", "Final Convergence", 1.00, "Connect earlier material into a coherent final musical statement."),
    ("LANDING", "Clear Ending / DJ Exit", 0.48, "Give the musical event a deliberate endpoint or documented DJ exit.")
)
WEIGHTS = (14, 24, 30, 24, 18, 34, 38, 18)  # 200 relative units, not a song duration
# Phase dynamics are proposed qualitative design values, never measured energy.
LAYERS = {
    "LOW": {
        "field": "motor",
        "related": ("FORWARD_MOTION", "LOW_ANCHOR", "BASS_SWING"),
        "function": "Physical kick/bass motor and timing reference",
    },
    "MID": {
        "field": "mid",
        "related": ("DENSE_LAYERS", "REPETITION", "VARIATION", "TENSION", "RELEASE"),
        "function": "Harmonic, rhythmic and timbral conversation",
    },
    "HIGH": {
        "field": "high",
        "related": ("SPATIAL_MOTION", "DYNAMIC_CONTRAST"),
        "function": "Spatial detail, perceptual movement and tension",
    },
    "VOICE": {
        "field": "voice",
        "related": ("VOICE_CLARITY", "VOCAL_PRESENCE"),
        "function": "Human meaning and foreground/background character",
    },
}

def _bar_allocation(total):
    if total is None:
        return [None] * len(PHASES)
    if isinstance(total, bool) or not isinstance(total, int) or not 32 <= total <= 2048:
        raise ValueError("INVALID_BAR_TARGET")
    # Deterministic largest remainder method: exact target, no phantom bars.
    weights = [x / sum(WEIGHTS) * total for x in WEIGHTS]
    base = [int(n) for n in weights]
    remaining = total - sum(base)
    for i in sorted(range(len(weights)), key=lambda i: (-(weights[i] - base[i]), i))[:remaining]:
        base[i] += 1
    return base

def assess(intent, semantic_result, causal_result, total_bars=None):
    if not all(isinstance(x, dict) for x in (intent, semantic_result, causal_result)):
        raise ValueError("INVALID_PREANALYSIS_INPUT")
    if semantic_result.get("system_id") != "666TDI-001" or causal_result.get("system_id") != "666TDI-001":
        raise ValueError("FOREIGN_ANALYSIS_NOT_ALLOWED")
    active = {x.get("id") for x in semantic_result.get("functions", [])
              if x.get("status") in ("SUPPORTED", "SUPPORTED_AND_CONSTRAINED")}
    allocated = _bar_allocation(total_bars)
    chapters = []
    cursor = 0
    for index, ((phase, label, energy, reason), bars) in enumerate(zip(PHASES, allocated)):
        start = cursor if bars is not None else None
        if bars is not None:
            cursor += bars
        # These are questions, not prescribed sounds or inferred story chapters.
        support = {
            "OPENING": ("LOW_ANCHOR", "REPETITION"),
            "MOTION": ("FORWARD_MOTION", "LOW_ANCHOR"),
            "DEVELOPMENT": ("VARIATION", "REPETITION", "SPATIAL_MOTION"),
            "TENSION": ("TENSION", "DENSE_LAYERS"),
            "CONTRAST": ("DYNAMIC_CONTRAST",),
            "RETURN": ("RELEASE", "VARIATION"),
            "CONVERGENCE": ("TENSION", "RELEASE", "VOICE_CLARITY"),
            "LANDING": ("FINALITY",),
        }[phase]
        witnesses = sorted(set(support) & active)
        chapters.append({
            "index": index + 1, "id": phase, "label": label, "relative_energy": energy,
            "relative_energy_type": "ILLUSTRATIVE_DESIGN_HYPOTHESIS",
            "bars": bars, "start_bar_zero_based": start,
            "end_bar_exclusive": cursor if bars is not None else None,
            "reason": reason, "supported_by_functions": witnesses,
            "status": "EVIDENCE_SUPPORTED_CANDIDATE" if witnesses else "OPTIONAL_CREATOR_REVIEW",
            "audio_measured": False,
        })
    layer_matrix = []
    for name, config in LAYERS.items():
        value = intent.get(config["field"], "")
        available = bool(isinstance(value, str) and value.strip())
        witnesses = sorted(active.intersection(config["related"]))
        layer_matrix.append({
            "layer": name, "source_field": config["field"], "provided": available,
            "musical_role": config["function"], "supported_functions": witnesses,
            "status": "DECLARED_AND_INTERPRETED" if available and witnesses else
                      "DECLARED_REQUIRES_REVIEW" if available else "UNSPECIFIED",
            "not_measured": True,
        })
    relations = []
    for rel in causal_result.get("relations", []):
        relations.append({
            "functions": rel.get("functions", []),
            "relation": rel.get("relation", "UNSPECIFIED"),
            "reason": rel.get("rationale", ""),
            "evidence": rel.get("evidence", {}),
            "status": "CAUSAL_RULE_HYPOTHESIS_NOT_AUDIO_PROOF",
        })
    alternatives = []
    for item in causal_result.get("emergences", []):
        alternatives.append({
            "id": item["id"], "functions": item["functions"],
            "option_a": {"name": "Preserve relationship", "effect": item["effect"]},
            "option_b": {"name": "Change arrangement or timing", "tradeoff": item["counterfactual"]},
            "evidence": item["evidence"],
            "creator_selection_required": True, "automatic_choice": False,
        })
    bpm = intent.get("bpm")
    if total_bars is not None and isinstance(bpm, int) and not isinstance(bpm, bool) and bpm > 0:
        # Explicit 4/4 PLANNING convention; not a prediction of Suno output.
        seconds = round(total_bars * 4 * 60 / bpm, 2)
        time_status = "THEORETICAL_4_4_PLANNED_BARS_NOT_RENDER_DURATION"
    else:
        seconds = None
        time_status = "NO_DURATION_INFERRED"
    from .musical_forces import derive
    return {
        "musical_forces": derive(intent, semantic_result, causal_result),
        "schema": SCHEMA, "system_id": "666TDI-001",
        "method": "RULE_DERIVED_FROM_EXISTING_R09_R10_MUSICAL_ANALYSIS",
        "status": "VISUAL_PREANALYSIS_CANDIDATE",
        "device_independent": True, "bar_target": total_bars,
        "planned_duration_seconds": seconds, "duration_status": time_status,
        "chapters": chapters, "layers": layer_matrix, "relations": relations,
        "alternatives": alternatives, "audio_verified": False,
        "renderer_executed": False, "creator_review_required": True,
        "no_story_invention": True, "read_only": True,
        "limitations": [
            "CHAPTERS_ARE_PROPOSED_NOT_RENDERED",
            "ENERGY_VALUES_ARE_ILLUSTRATIVE_NOT_MEASURED",
            "STORY_SPECIFIC_EVENTS_NOT_INFERRED",
            "ONLY_EXPLICIT_BAR_TARGET_PRODUCES_BAR_COUNTS",
            "FOUR_FOUR_TIMING_IS_THEORETICAL_NOT_SUNO_DURATION",
            "NO_AUTONOMOUS_COMPOSER_OR_GLOBAL_LEARNING"
        ],
    }
