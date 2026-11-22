"""Validated configuration models; no arbitrary commands or executable config."""
from dataclasses import dataclass, field
from typing import Literal

MetricName = Literal["cpu", "memory", "disk_read", "disk_write", "network_rx", "network_tx"]
LedName = Literal["caps", "num", "scroll"]
METRICS = ("cpu", "memory", "disk_read", "disk_write", "network_rx", "network_tx")
LEDS = ("caps", "num", "scroll")

@dataclass(frozen=True)
class Rule:
    metric: MetricName
    led: LedName
    threshold: float
    def validate(self):
        if self.metric not in METRICS or self.led not in LEDS:
            raise ValueError("Unknown metric or LED")
        if not (0 <= self.threshold <= 1_000_000_000):
            raise ValueError("threshold outside accepted range")
        if self.metric in ("cpu", "memory") and self.threshold > 100:
            raise ValueError("percentage cannot exceed 100")

@dataclass(frozen=True)
class Config:
    interval: float = 0.5
    hardware: bool = False
    rules: tuple[Rule, ...] = field(default_factory=lambda: (
        Rule("cpu", "caps", 75),
        Rule("disk_write", "scroll", 2048),
        Rule("network_rx", "num", 4096),
    ))
    def validate(self):
        if not 0.2 <= self.interval <= 60:
            raise ValueError("interval must be 0.2..60 seconds")
        if len(self.rules) > 30:
            raise ValueError("too many rules")
        for r in self.rules:
            r.validate()
