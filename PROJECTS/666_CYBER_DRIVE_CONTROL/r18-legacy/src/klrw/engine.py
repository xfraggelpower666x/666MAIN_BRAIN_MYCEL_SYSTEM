"""Rules are OR-combined per LED. Deterministic tick-based engine."""
from .model import Config, LEDS

class RuleEngine:
    def __init__(self, cfg: Config, backend):
        cfg.validate()
        self.cfg = cfg
        self.backend = backend
        self.active = {led: False for led in LEDS}

    def tick(self, sample):
        desired = {led: False for led in LEDS}
        for rule in self.cfg.rules:
            if getattr(sample, rule.metric) >= rule.threshold:
                desired[rule.led] = True
        for led, enabled in desired.items():
            if self.active[led] != enabled:
                self.backend.apply(led, enabled)
                self.active[led] = enabled
        return desired

    def close(self):
        try:
            for led in LEDS:
                if self.active[led]:
                    self.backend.apply(led, False)
                    self.active[led] = False
        finally:
            self.backend.close()
