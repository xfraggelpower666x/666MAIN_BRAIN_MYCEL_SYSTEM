# 666SOUNDsDESIGn · CONTENT INTELLIGENCE ARCHIVE R03

**Electron desktop catalog + isolated Python/SQLite engine**. This is a new additive project; the original FULL LYRICS TOOL V2.2 R02 is retained verbatim in `legacy_r02/` and is not rewritten.

## Windows start (one CMD only)

Double-click `START.cmd`. The launcher checks for Node.js and Python and installs **only missing Electron npm dependencies** for this new app. It does **not** silently install/upgrade system-wide Node.js or Python. If absent, the launcher gives an installation hint. Optional `pypdf` and `python-docx` are checked from **System & Dependencies**, and installed only upon confirmation. Network may be required for npm/PyPI.

Manual alternative:

```powershell
npm install --no-audit --no-fund
npm start
```

Recommended: Node.js LTS and Python 3.11+. An internet connection is required for first-time Electron installation, not for normal local import/export. Keep `legacy_r02/` intact. Start from the extracted folder, not directly inside ZIP.

## Major features

- Neon-purple/pink/cyan/dark-gray desktop dashboard with live database counters.
- Browser selection and drag & drop for multiple local files and ZIP backups.
- Text/Markdown/JSON/JSONL/code/logs/CSV/XML/YAML/TOML and other plain text; PDF and DOCX when optional libraries are installed. Unknown/binary files recorded with `unextracted` status and not falsely decoded.
- ChatGPT-style conversation exports supported via `mapping/message/content.parts` or `messages` structures. Text-based projects and tags are inferred as **suggestions**.
- 120+ titled songs in one document: structural `Title:` headers are split into discrete records and written as individually addressable JSON files. Unstructured input is never cut at arbitrary character counts, to avoid silent song mixing.
- SQLite catalog and per-project `index.json`, `project_report.json`, global index plus one JSON per inserted record. Full-text browser, one-click whole-content copy, project filters, JSON/Markdown/ZIP export.
- ZIP old-archive with explicit record selection and CRC verification; active records flagged archived, not deleted.
- Optional read-only import of the legacy 1,915-row lyrics database.

## Data layout

**Runtime data**, distinct from source, lives in Electron's per-user `userData/catalog-data/`, opened using `System` > storage folder.

```
catalog-data/
  catalog.sqlite                  # source of truth and indexed queries
  records/PROJECT/HASH.json       # materialized, canonical record content
  index/index.json                # root metadata, no text re-read
  index/PROJECT/index.json        # project pointers and category counts
  index/PROJECT/project_report.json
  exports/                        # non-overwriting timestamped exports
  old_archive/                    # verified ZIP preservation
```

Each record has category (lyrics, style_prompt, prompt, framework, code, diverse), project, source name/hash, classification confidence, topics and timestamps. Source files themselves are not preserved by the new importer. The legacy R02 folder is included only as an original, manually migratable source. Archive ZIPs are permanent until explicitly removed outside the tool.

## Trust and limits

- This version is a **local development candidate**, not a Windows production-tested executable.
- Classification is deterministic heuristics, not AI/NLP and not guaranteed accurate. Project-level reports are candidate recommendations, **not** verified comparisons against the live GitHub repositories.
- ZIPs: max 2,000 entries, max 25 MiB per nested entry, 150 MiB extracted total; suspicious compression ratios and traversal paths are rejected. Direct files max 150 MiB, with textual parsing max 25 MiB; limits are configured in `engine/bridge.py`.
- Very large/complex, scanned or password-protected PDF files, PAGES, audio/video or proprietary formats are not universally readable; these are logged as `unextracted`. OCR is not implemented.
- Import records cannot be overwritten by re-import; hash duplicate keys retain project and category context. No native repository writes and no auto-synchronization.
- Unknown project classification is `UNASSIGNED`. Manual per-record editing, stronger entity linking, secure multi-job background processing and actual native-system diff remain future enhancements.
- New data should be backed up regularly using JSON/ZIP exports and OS backups; exports are not a substitute for disaster recovery of the userData folder.

## Validation

```powershell
npm run check
npm test
```

Tests include 120-song split, duplicate avoidance, chat backup extraction, ZIP safety, archival readback, legacy read-only migration, export, unknown formats and project routing.

## Native integration

This project is not uploaded to GitHub. Its folder can be added to a chosen repository only after current HEAD, authority, permissions and regression checks. A project detected in a backup does not activate that project's runtime.


### R05.2 Reparatur
Der zentrale Starter erkennt jetzt den Fall eines blockierten Electron-Postinstall-Skripts und führt nach Zustimmung eine gezielte Runtime-Reparatur aus. Keine globalen npm-Freigaben.


### R05.3 — npm allowScripts / Electron Runtime
Die frühere Runtime-Reparatur war unvollständig: sie führte `install.js` aus,
ohne zuerst die von npm gemeldete Projekt-Skriptfreigabe zu behandeln. R05.3
fragt gezielt `electron` frei, baut das Paket per `npm rebuild electron` neu
und kontrolliert `dist/electron.exe`/`path.txt`. Bei weiterem Fehlschlag zeigt
der Starter konkrete Download-/Proxy-Hinweise statt einer pauschalen Meldung.


### R06.1
Gezielte Korrektur des nachweisbaren Electron-ENOENT-Fehlers durch CRLF in `node_modules/electron/path.txt`. Der Starter bereinigt vorhandene Marker ohne erneuten Runtime-Download.


## Electron Desktop UI polish — R06.1 additive presentation update

- R06.1 ist bereits eine Electron-Desktop-Anwendung (main/preload + HTML/CSS/JS renderer); kein Frameworkwechsel.
- Neues neon-cyber Desktop-Metaband, aktueller R06.1-Schriftzug statt altem R03-Label, Kontrast-/Fokusverbesserungen und responsive Layoutanpassungen.
- Keine IPC-, Datenbank-, Import-, Archiv-, Starter- oder Build-Verhaltensänderungen. Alle bestehenden HTML-Element-IDs und Event-Handler bleiben erhalten.
- Bestehende erfolgreiche Windows-R06.1-Bestätigung gilt für die unveränderte Laufzeitbasis; die UI-Erweiterung ist noch nicht am Windows-Host abgenommen.
