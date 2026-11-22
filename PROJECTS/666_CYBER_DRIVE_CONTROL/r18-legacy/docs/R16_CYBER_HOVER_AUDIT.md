# R16 Cyber Hover — Audit und Handoff

## Geprüfte Basis
R15-CYBER-OVERLAY (lokaler Code), additive Entwicklungsvariante, kein GitHub-Write.

## Änderungen
- `src/klrw/drive_workspace.py`: `minimal` als zusätzliches gespeichertes Layout. Bestehende JSON-Schema-Version und andere Einstellungen bleiben unverändert.
- `src/klrw/drive_workspace_window.py`: dritte vertikale Minimalansicht mit Laufwerksbuchstabe + nur einer Bicolor-LED pro Laufwerk, anzeigebasierte Hover-Bereiche, read-only detailliertes Tooltip (Label, Dateisystem, Read/Write, Messzuordnung). Auch horizontale/vertikale Ansichten haben Tooltip.
- `tests/test_r16_hover_overlay.py`: neue Minimal-/Speicher-/Hover-Regression.
- Konfiguration `led_hold_ms=180`, `led_quiet_ms=450`, `activity_threshold_bps=4096` aus R15 beibehalten, keine unautorisierte Änderung der laufenden Benutzerkonfiguration.

## Technische Grenzen
- GUI und Hover unter Windows sind noch nicht praktisch abgenommen.
- LED-Farbwechsel erfolgt im vorhandenen ca. 500-ms-Sampler-Takt; `hold_ms` < 500 ms kann sichtbar übersprungen werden. Dieser Umstand bleibt ein offener Verbesserungspunkt; kein Hardware-Readback.
- Physische USB-Tastatur-HID-Steuerung bleibt deaktiviert.

## Ausgeführte Tests
`PYTHONPATH=src python -m pytest -q --disable-warnings --maxfail=1`: 279 passed; Python compileall erfolgreich.

## Windows-Abnahme
Batch `START_WINDOWS_MENUE.bat`, Menü E, Layout `minimal` wählen, Anwenden, Overlay zeigen; Hover, Speichern und Wiederstart manuell prüfen.

## Status
LOCAL CODE VERIFIED; WINDOWS HOST READBACK_PENDING.
