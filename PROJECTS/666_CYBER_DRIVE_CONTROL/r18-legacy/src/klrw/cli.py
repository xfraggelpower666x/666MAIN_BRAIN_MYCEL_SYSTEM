"""Console entry point with explicit hardware consent on each launch."""
import argparse
import json
import sys
from pathlib import Path
from dataclasses import replace
from .config import load, save
from .model import Config
from .runtime import Monitor
from .ssd import IndicatorSettings, indicator_hex

def main(argv=None):
    parser = argparse.ArgumentParser(description="Windows Keyboard LED Remapper")
    parser.add_argument("--config", type=Path, default=Path("klrw.json"))
    parser.add_argument("--init-config", action="store_true")
    parser.add_argument("--hardware", action="store_true", help="Explicitly alter real lock-key states; may affect typing")
    parser.add_argument("--ssd-led", action="store_true", help="Show read/write virtual SSD indicator")
    parser.add_argument("--disk", default="_total", help="psutil disk device ID, or _total")
    parser.add_argument("--saturation-kib", type=float, default=1024., help="KiB/s for full LED brightness")
    parser.add_argument("--count", type=int, default=0, help="0 = run until Ctrl+C")
    args = parser.parse_args(argv)
    if args.count < 0:
        parser.error("count must not be negative")
    if args.init_config:
        if args.config.exists():
            parser.error("Configuration exists; refusing overwrite")
        save(args.config, Config())
        print(f"Created {args.config}")
        return 0
    try:
        cfg = load(args.config) if args.config.exists() else Config()
        # Config alone cannot activate hardware. Requires an explicit CLI flag.
        cfg = replace(cfg, hardware=args.hardware)
        if cfg.hardware and sys.platform != "win32":
            parser.error("Hardware backend only works on native Windows")
        settings = IndicatorSettings(args.disk, args.saturation_kib)
        settings.validate()
        mon = None
        def output(sample, states):
            payload = {"metrics": vars(sample), "leds": states}
            if args.ssd_led:
                payload["ssd"] = {"rates": vars(mon.disk_rates), "color": indicator_hex(mon.disk_rates, settings)}
            print(json.dumps(payload), flush=True)
        mon = Monitor(cfg, on_update=output, indicator_settings=settings)
        try:
            mon.run(count=args.count or None)
        except KeyboardInterrupt:
            mon.stop_event.set()
        if mon.error:
            print(f"Monitor failure: {mon.error}", file=sys.stderr)
            return 1
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
