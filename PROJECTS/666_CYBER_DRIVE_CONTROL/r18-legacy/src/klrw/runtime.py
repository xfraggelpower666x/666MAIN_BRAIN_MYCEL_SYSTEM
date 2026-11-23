"""Background polling separated from UI and command layer."""
import threading
import logging
from .metrics import SystemSampler
from .engine import RuleEngine
from .leds import PreviewBackend, WindowsLockBackend
from .ssd import DiskActivitySampler, IndicatorSettings, DiskRates

log = logging.getLogger(__name__)

class Monitor:
    def __init__(self, cfg, on_update=lambda sample, state: None, sampler=None, backend=None,
                 disk_sampler=None, indicator_settings=None):
        cfg.validate()
        self.cfg = cfg
        self.sampler = sampler or SystemSampler()
        self.backend = backend or (WindowsLockBackend() if cfg.hardware else PreviewBackend())
        self.engine = RuleEngine(cfg, self.backend)
        self.on_update = on_update
        self.disk_sampler = disk_sampler or DiskActivitySampler()
        self.indicator_settings = indicator_settings or IndicatorSettings()
        self.indicator_settings.validate()
        self.disk_rates = DiskRates(self.indicator_settings.device, 0., 0.)
        self.stop_event = threading.Event()
        self.worker = None
        self.error = None

    def run(self, count=None):
        runs = 0
        try:
            while not self.stop_event.is_set() and (count is None or runs < count):
                sample = self.sampler.sample()
                state = self.engine.tick(sample)
                try:
                    self.disk_rates = self.disk_sampler.sample(self.indicator_settings.device)
                except (OSError, RuntimeError, KeyError, ValueError):
                    log.exception("Disk indicator unavailable; continuing system monitor")
                    self.disk_rates = DiskRates(self.indicator_settings.device, 0., 0.)
                try:
                    self.on_update(sample, state)
                except Exception:
                    log.exception("Update callback failed")
                runs += 1
                self.stop_event.wait(self.cfg.interval)
        except Exception as exc:
            self.error = exc
            log.exception("Monitor stopped on error")
        finally:
            self.engine.close()

    def start(self):
        if self.worker is not None:
            raise RuntimeError("Monitor already started")
        self.worker = threading.Thread(target=self.run, name="KLRW-monitor", daemon=False)
        self.worker.start()

    def stop(self, timeout=5):
        self.stop_event.set()
        if self.worker and threading.current_thread() != self.worker:
            self.worker.join(timeout=timeout)
            if self.worker.is_alive():
                raise TimeoutError("Monitor thread is still running")
