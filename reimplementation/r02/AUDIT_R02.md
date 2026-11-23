# R02 · Test- und Implementierungsabnahme (22.11.2026)

**Projekt:** `666 RESEARCH MD DATABASE ORCHESTRA` · **Scope:** neue getrennte `reimplementation/r02`, keine Änderung der historischen Originale, Manifeste, Freezes, R01-Quelltexte oder fremder Projekte.

## Ausgangsbasis

- Stand beim Start: GitHub `666MAIN_BRAIN` + verifiziertes R01; die Originale sind drei SHA-256-verifizierte JavaScript-Quellmodule.
- Historischer Audit `v1.7.1` ist **Dokumentation**, kein derzeit erfolgreicher Original-Runtime-Readback.
- R01: `node --test reimplementation/r01/tests/runtime.test.js` → **20/20 PASS**.

## Neue Schnittstellen

- `src/bootstrap.js` bindet nach dem R01-SHA-/Quellenaudit die read-only Research-Funktionen an.
- `src/blind_ab.js` enthält ein in-memory, schema-validiertes State Machine für Blind-A/B.
- `cli.js` bietet nur `status`, `search`, `get`, ohne beliebige Schreibbefehle.

## Testbelege

- `node --test reimplementation/r02/tests/blind_ab.test.js`: **23/23 PASS**.
- Baseline R01: **20/20 PASS**.
- Syntaxcheck: `node --check` für neuen Runtime-/CLI-Code: PASS.
- `node reimplementation/r02/cli.js status`: berichtet `production=false`, `historicalReadback=PENDING`, `topics=2`, `entries=28`, `sources=25`, `prompts=1`.
- Keine Nutzerstems und keine echten A/B-Audios getestet.

## Negativfälle

- Unvollständiger Bewertungsstand kann nicht gelockt oder entblindet werden.
- `NaN`, `Infinity`, `null`, Strings, Werte unter 0 oder über 100 werden blockiert.
- Fehlende/zusätzliche Kriterien, unbekannte Prüfer, doppelte Bewertungen oder manipulierte Import-States werden blockiert.
- Bekannte Audio-Dateinamen und Kandidaten-Parameter fehlen im Evaluator-Packet.
- Unbekannte CLI-Schreibbefehle bleiben blockiert.

## Offene Sicherheitsgrenzen

- Betreiberdatei und `operatorManifest()` enthalten sensible Zuordnung und sind **nicht** für Bewertende bestimmt.
- Aufrufende App muss Mediendateien separat anonymisieren, Zugriffskontrolle schaffen und Speicherung gegen Manipulation absichern.
- Keine Freigabe für produktive Blind-A/B-Sitzungen mit echten Dateien ohne unabhängigen Host-Test.

## Freeze-Entscheidung

**R02-CANDIDATE_LOCAL_PASS; vollständige alte v1.7.1-Runtime READBACK_PENDING; NO_PRODUCTION_FREEZE.**

Diese Datei dokumentiert lokale Codeprüfungen, nicht den GitHub-Commit-Readback. Ein nachfolgender GitHub-Readback ist separat zu erfassen.
