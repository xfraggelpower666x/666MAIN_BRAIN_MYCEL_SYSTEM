"""Lokale, unabhängige Musikarchitektur; keine GitHub-Mutationen."""
from dataclasses import dataclass, field, asdict
from typing import Optional
import json

@dataclass
class MusicalIntent:
    title: str
    genre: str
    bpm: int
    motor: str
    mid: str
    high: str
    atmosphere: str
    energy: str
    voice: str = ""
    lyrics: str = ""
    structure: str = ""
    psychoacoustics: str = ""
    ending: str = ""
    avoid: str = ""
    target_seconds: Optional[int] = None
    emphasis: dict = field(default_factory=dict)

# Nur historisch dokumentierte Grenzen; nicht als aktuelle Plattformverifikation verwenden.
SPECS = {
    "asg_main": {"fields": {"title": None, "style": None, "lyrics": None}, "max_seconds": None, "source_status": "historical_unknown_limits"},
    "ace_step_asg": {"fields": {"title": 80, "style": 1000, "lyrics": 3002}, "max_seconds": 240, "source_status": "historical_2026_09"},
    "lyria2_asg": {"fields": {"title": 80, "description": 400, "negative": 100}, "max_seconds": 32, "source_status": "historical_2026_09"},
    "elevenlabs_asg": {"fields": {"title": 80, "style": None, "description": None}, "max_seconds": 300, "source_status": "historical_2026_09"},
    "suno_reference": {"fields": {"title": 80, "extended": 800, "style": 1000, "lyrics": 5000}, "max_seconds": None, "source_status": "local_reference_not_live_verified"},
}

# Bedeutungsträger statt willkürlicher Zeichenschnitte. Kerninformationen werden nicht still entfernt.
PRIORITY = ["genre", "bpm", "motor", "energy", "mid", "high", "psychoacoustics", "voice", "atmosphere", "structure", "ending"]
LABELS = {"genre":"Genre", "bpm":"Tempo", "motor":"Motor", "energy":"Energy", "mid":"Mid", "high":"High", "psychoacoustics":"Psychoacoustics", "voice":"Voice", "atmosphere":"Atmosphere", "structure":"Structure", "ending":"Ending"}

def semantic_pack(intent: MusicalIntent, limit: Optional[int]):
    """Nimmt nur vollständige Bedeutungseinheiten; bei Überlauf gibt es explizite Verluste."""
    selected, omitted = [], []
    fields = sorted(PRIORITY, key=lambda k: (-intent.emphasis.get(k, 0), PRIORITY.index(k)))
    for field in fields:
        value = getattr(intent, field)
        if value is None or value == "":
            continue
        fragment = f"{LABELS[field]}: {value}"
        candidate = "; ".join(selected + [fragment])
        if limit is None or len(candidate) <= limit:
            selected.append(fragment)
        else:
            omitted.append({"field": field, "reason": "budget_overflow", "required_chars": len(fragment)})
    return "; ".join(selected), omitted

def compile_intent(intent: MusicalIntent, renderer: str):
    if renderer not in SPECS:
        raise ValueError(f"Unbekannter Renderer: {renderer}")
    spec = SPECS[renderer]
    result = {"renderer": renderer, "source_status": spec["source_status"], "fields": {}, "warnings": [], "omissions": []}
    if not 1 <= intent.bpm <= 350:
        raise ValueError("BPM außerhalb des lokalen Validierungsbereichs")
    if intent.target_seconds and spec["max_seconds"] and intent.target_seconds > spec["max_seconds"]:
        result["warnings"].append("DURATION_EXCEEDS_HISTORICAL_RENDERER_LIMIT")
    max_title = spec["fields"].get("title")
    if max_title and len(intent.title) > max_title:
        result["warnings"].append("TITLE_OVER_BUDGET_NO_SILENT_TRUNCATION")
    result["fields"]["title"] = intent.title
    if renderer == "lyria2_asg":
        result["fields"]["description"], omitted = semantic_pack(intent, spec["fields"]["description"])
        result["omissions"].extend(omitted)
        neg = intent.avoid
        if len(neg) > spec["fields"]["negative"]:
            result["warnings"].append("NEGATIVE_OVER_BUDGET_NO_SILENT_TRUNCATION")
        result["fields"]["negative"] = neg
        if intent.lyrics:
            result["omissions"].append({"field":"lyrics", "reason":"not_supported_in_local_lyria_mapping"})
    else:
        f = "description" if renderer == "elevenlabs_asg" else "style"
        result["fields"][f], omitted = semantic_pack(intent, spec["fields"].get(f))
        result["omissions"].extend(omitted)
        if renderer == "suno_reference":
            result["fields"]["extended"] = ""
        if "lyrics" in spec["fields"]:
            result["fields"]["lyrics"] = intent.lyrics
            cap = spec["fields"]["lyrics"]
            if cap and len(intent.lyrics) > cap:
                result["warnings"].append("LYRICS_OVER_BUDGET_NO_SILENT_TRUNCATION")
        elif intent.lyrics:
            result["omissions"].append({"field":"lyrics", "reason":"no_verified_lyrics_mapping"})
    for key, val in result["fields"].items():
        cap = spec["fields"].get(key)
        if cap is not None and len(val) > cap:
            result["warnings"].append(f"FIELD_OVER_LIMIT:{key}:{len(val)}>{cap}")
    if result["omissions"]:
        result["warnings"].append("SEMANTIC_INFORMATION_NOT_RENDERED")
    result["status"] = "PARTIAL" if result["warnings"] else "COMPILED_UNVERIFIED_AUDIO"
    result["audit"] = {"source_fields": list(asdict(intent).keys()), "rendered_field_lengths": {k:len(v) for k,v in result["fields"].items()}, "real_audio_tested":False}
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv)!=3:
        raise SystemExit("Aufruf: python src/music_arch.py examples/intent.json lyria2_asg")
    with open(sys.argv[1], encoding="utf-8") as f:
        intent=MusicalIntent(**json.load(f))
    print(json.dumps(compile_intent(intent, sys.argv[2]), indent=2, ensure_ascii=False))
