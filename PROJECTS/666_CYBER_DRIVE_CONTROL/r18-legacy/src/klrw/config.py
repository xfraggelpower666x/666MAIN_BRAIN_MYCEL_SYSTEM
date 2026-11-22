"""Versioned JSON load/save. Never loads pickle or executes scripts."""
import json
from pathlib import Path
from .model import Config, Rule

SCHEMA = 1

def load(path: Path) -> Config:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("Unsupported config schema")
    if set(data) - {"schema", "interval", "hardware", "rules"}:
        raise ValueError("Unknown configuration keys")
    rules = data.get("rules", [])
    if not isinstance(rules, list):
        raise ValueError("rules must be a list")
    for r in rules:
        if not isinstance(r, dict) or set(r) != {"metric", "led", "threshold"}:
            raise ValueError("Invalid rule structure")
    if type(data.get("hardware", False)) is not bool:
        raise ValueError("hardware must be a bool")
    cfg = Config(interval=float(data.get("interval", 0.5)),
                 hardware=data.get("hardware", False),
                 rules=tuple(Rule(**r) for r in rules))
    cfg.validate()
    return cfg

def save(path: Path, cfg: Config) -> None:
    cfg.validate()
    data = {"schema": SCHEMA, "interval": cfg.interval, "hardware": cfg.hardware,
            "rules": [vars(r) for r in cfg.rules]}
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
