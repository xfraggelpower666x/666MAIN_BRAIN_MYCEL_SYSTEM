# R6 Integrationsaudit

## Externe Quelle

`EloyEMC/Multi-color-LED-indicator-for-Silakka54-with-RP2040-Zero`, main, `README.md`, `TECHNICAL.md`, `keymap.c`, `config.h`, `rules.mk` über GitHub gelesen.

- QMK RGBLIGHT layers / WS2812 (GP16) / RP2040-Zero: **verifiziert in Quelle**.
- Priorität Caps Lock rot > Layer 3 violett > Layer 2 grün > Layer 1 blau, Base aus: **verifiziert**.
- Unabhängige bzw. synchronisierte Hälften: **verifiziert**. Firmware benötigt gleiche Bauvariante an beiden Controllern.
- Kein dokumentierter allgemeiner Windows-HID-RGB-Steuerungsvertrag: **OFFEN**.
- GitHub-Lizenz MIT, `config.h` GPL-Notice: **CONFLICT_QUARANTINE für eventuelle Originalcode-Übernahme**. Kein Originalcode übernommen.

## Änderungen gegenüber R5

Additiv: `src/klrw/rgb_layers.py`, `src/klrw/rgb_cli.py`, `tests/test_rgb_layers.py`, CLI-Entrypoint in `pyproject.toml`, README-Zusatz. Alle übrigen bestehenden `src/klrw/*.py` unverändert.

## Sicherheitsgrenzen

Nur Farbpolitik und Vorschau. Kein Flashen, kein USB/HID/Serial-Zugriff, kein EEPROM, keine realen Lock-Key-Veränderungen durch R6. `open_rgb_hardware` lehnt unbekannte Hardware mit Fehler ab.

## Abnahme

Tests lokal auf Linux-Runner mit pytest, Hardware/Windows readback **READBACK_PENDING**. Weitere Beobachtungen im `TESTBERICHT_R6.md`.
