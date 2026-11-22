# R5 Integration Audit · 2026-11-21

## Source evidence
- https://github.com/jwilk-archive/python-keyboardleds
- Branch master, archived = true, LICENSE MIT.
- `keyboardleds.py`: `LedKit`, `Led`, Linux `fcntl.ioctl` KDGETLED/KDSETLED; Linux EV_LED event protocol; Python raises `NotImplementedError` on non-Linux.

## Assessment
A direct Windows port of ioctl and evdev code is unsupported. We independently implemented the object-oriented API idea in a new device-neutral, simulation-first `klrw.ledkit` module.

## Changes
- `src/klrw/ledkit.py`: standalone LedKit facade, per-LED Light objects, capability flags, read/set/reset/toggle, atomic-scoped best-effort group changes with reverse rollback and explicit exceptions.
- `tests/test_ledkit.py`: ten regression tests for operations, validation, capabilities, failure recovery, and safe simulation.
- `pyproject.toml`: 1.4.0.
- `README.md`: integration documentation.

## Non-changes
- No change to old `manual.py`, `leds.py`, `engine.py`, GUI or CLI.
- No Windows native device driver and no Linux-only execution dependency.
- No automatic hardware activation. No upstream modification.

## Limits
- Windows lock state is not proof of independently controllable physical LED.
- Rollback is best-effort; hardware/OS state could change concurrently.
- No native Windows GUI/physical keyboard readback in Linux test environment.
- No part of archived source code was copied; conceptual interface design only.

## Status
Linux-environment unit regression VERIFIED; Windows hardware READBACK_PENDING.
