# Wiederaufnahme offener Research-Orchestra-Aufgaben

## Belegter Ist-Stand

- Historischer Release: `v1.7.1-clean-system.1` (dokumentiert, im neuen Arbeitsbaum NICHT vollständig rehydriert).
- Das historische SHA-256-Dateimanifest enthält 136 Prüfeinträge.
- 10 historische, zum Manifest passende MD-Dateien und 3 Original-JS-Dateien sind vorhanden; die Manifestdatei selbst ist eigenständige Kontrollbasis.
- Die 3 JS-Dateien sind bytegenau zum historischen v1.7.1-Manifest passend, nicht bloß thematisch ähnlich.
- Das ursprüngliche `system/bootstrap-loader.js`, die `system/core`- und `system/modules`-Linie, das `package.json`, die Originaltests und Python-Audio-Tools sind nicht wiederhergestellt.

## Weiterentwicklung ohne Verlust

Arbeitsfähige Prüfroutine und eigene Tests sind vorhanden. Fehlende Module dürfen neu entwickelt werden, aber nur als **neue, getrennte Implementierung** mit eigener Kennung; nicht als historisch wiedergefundenes v1.7.1-Original. Die Quellenprüfung ist fail-closed.

## Freigabegates

`READBACK_PASS` → `ORIGINAL_RUNTIME_TESTS_PASS` → `SECURITY_AND_CONTENT_AUDIT_PASS` → `FREEZE` → `SYSTEM_ONLY_BACKUP`

Bis alle Gates belegbar sind: `PARTIAL · READBACK_PENDING · NO_PRODUCTION_PROMOTION`.
