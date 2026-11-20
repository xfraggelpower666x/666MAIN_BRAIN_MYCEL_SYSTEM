# v1.10.5 (2026-11-14)

- SSR-Transcript-Fallback für Windows ergänzt.
- Windows-Laufzeitprüfung an die ausgelieferte PYw-GUI und den Bootstrap-Interpreter gebunden.
- Äußeres PC-Manifest in die Release-Prüfung aufgenommen.
- Scriptable v1.0.9 mit gemeinsamer Importkette für regulären Import und Host-Abnahme eingebettet.

# Changelog

## 1.10.4 — 2026-11-07

- Embedded Scriptable companion advanced to v1.0.8 with one-step host acceptance.
- Added Windows end-to-end host acceptance probe: live Share fetch, parse, multi-format export and byte/readback receipt.
- Added cross-platform machine-readable acceptance receipt contracts.
- Release-integrity guards updated for PC v1.10.4 / mobile v1.0.8.
- Existing PC parser/GUI behavior preserved.

## 1.10.3 — 2026-11-06

- Current Source Mapping repaired: active Scriptable companion now points to v1.0.7 instead of stale v1.0.0.
- Added `CURRENT_RELEASE_INDEX.md` as explicit in-package current-state anchor.
- Added release-integrity regression tests for companion ZIP/hash/version/manifest and stale-current-reference guards.
- No PC parser/recovery behavior changed. No mobile runtime code changed.
- Real Windows/iPhone host gates remain pending until executed on those hosts.

## 1.10.3 — 2026-11-06

- Scriptable Companion auf v1.0.7 aktualisiert und bytegleich eingebettet
- v1.0.6 als History/Provenienz erhalten
- On-Device-Selbsttest und Public-Share-Kompatibilitätsprobe dokumentiert
- `VERIFY_WINDOWS_RUNTIME.bat` und maschinenlesbaren Windows-Runtime-Probe ergänzt
- GUI-Probe prüft Core, Backend, Tkinter, Pillow, reale `ChatBackupApp`, Titel und Geometrie
- Nicht-Windows-Probe schließt Windows-Gate ausdrücklich nicht
- bestehende PC-Parser-/Recovery-Architektur unverändert erhalten
- Bootstrap UTF-8-BOM / ASCII-Body / CRLF-Vertrag erhalten

## 1.10.1 — 2026-11-06

- Scriptable Companion von historischem v1.0.0 auf v1.0.6 synchronisiert
- Flight/SSR-Variantentoleranz und Source-Fingerprint des mobilen Zweigs integriert
- Companion-Bytegleichheit geprüft

## 1.10.0 — 2026-10-22

- aktuellen ChatGPT-Share-Bruch als `AUTH_WALL_DETECTED` modelliert
- Login-/Signup-Hülle wird vor den normalen Parser-Fallbacks erkannt
- kein irreführender „unsupported format“-Fehler mehr, wenn der Conversation-Payload gar nicht geliefert wurde
- neuer linker Menüpunkt `Browser Recovery / Browser-Recovery`
- automatischer Übergang in Browser Recovery nach erkanntem Auth-Wall
- geführter Ablauf: Share im angemeldeten Browser öffnen → sichtbaren Verlauf kopieren → Zwischenablage analysieren
- Browser-Recovery verwendet den bestehenden fail-closed Manual-/Gruppenchat-Parser
- Browser-Recovery liest keine Cookies und umgeht keine ChatGPT-Anmeldung
- `browser-assisted-transcript` als eigene Parser-Provenienz und `BROWSER_CLIPBOARD_RECOVERY` als Capture-Status
- Integritätsprofil führt `BROWSER_ASSISTED_RECOVERY` getrennt
- lange wiederhergestellte Transcripts werden weiterhin chunked in die GUI eingefügt
- neuer Regressionstest für Auth-Wall-Erkennung und Browser-Recovery
- bestehender Scriptable-iPhone-Companion bleibt gebündelt und separat versioniert

## 1.8.2 — 2026-10-21

- Direkter Einzelbild-Download im Chat-Bildbrowser und in der Großansicht.
- Batch-Download für ausgewählte Bilder und alle direkt erreichbaren Bilder.
- Batch-Ausgabe in frei wählbaren Zielordner mit kollisionssicheren Dateinamen.
- Verifizierter Binär-Write/Readback für heruntergeladene Bilder.
- Hilfe erklärt jetzt ausdrücklich, dass Portable-ZIP-Bilder echte Binärdateien in `assets/` sind und nicht Base64.
- Keine Änderung am fail-closed Verhalten für interne Asset-Pointer ohne erreichbare Bytes.

## 1.8.1 — 2026-10-20
- Audit/Repair der v1.8.0-Versionkohärenz; Bootstrap meldet nicht mehr fälschlich v1.7.0.
- README und Statusdateien auf den tatsächlichen Current gebracht.
- Strukturierte Assistant-/Custom-GPT-Identitäten bleiben erhalten.
- Participant-Deduplizierung auf stabile Identitäten gehärtet.
- Manual-Parser schützt normale Markdown-Überschriften vor falscher Teilnehmererkennung.
- Roundtrip-Unterstützung für exportierte Gruppen-Markdown-Transcripts erhalten.
- neue Regressionstests für die reparierten Risiken.

## 1.8.0
- Gruppenchat-/Mehrteilnehmer-Datenmodell ergänzt.
- Explizite Participant-IDs/Namen/Benutzernamen aus Share-Daten werden bewahrt.
- Manueller Gruppenchat-Parser für eindeutige Sprecherlabels ergänzt.
- Fail-closed Teilnehmerzuordnung: keine Identitätsvermutung.
- Machine JSON auf schemaVersion 1.3.0 erweitert.
- Structure Inspector auf schemaVersion 1.1.0 erweitert und zeigt Teilnehmerdaten.
- Hilfe EN/DE um Gruppenchat-Archivierung erweitert.

## 1.7.0 — 2026-10-20

- neuer linker Menüpunkt `Private / Manual` / `Privat / Manuell`
- private `/c/`-Links werden in den sicheren manuellen Import geroutet statt einen öffentlichen Download zu behaupten
- automatischer `manual-transcript`-Parser für komplett kopierten Chattext
- Rollenmarker-Recovery für English/Deutsch inklusive Markdown-Überschriften
- Fail-safe Fallback: ohne sichere Rollenmarker wird der vollständige Text als eine Nachricht erhalten; keine erfundenen Turns
- manuelle Transcript-Nachrichten erhalten IDs, Rollen, `rawContent`, Metadaten, Copy-/UI-Felder und Warnungen
- Structure Inspector unterstützt jetzt auch manuell analysierte/private Chat-Imports
- JSON/JSONL/Portable Backup erhalten strukturierte Manual-Chat-Nachrichten
- Markdown wird bei manuell analysierten Chats aus der rekonstruierten Nachrichtenstruktur erzeugt
- TXT/JavaScript nutzen normalisierten Transcript-Inhalt
- Hilfe in English/Deutsch stark erweitert: Share-Link kopieren, private Chats, manuelles Kopieren, Analyse/Export, Datenschutz und `Chat voll`-Workaround
- beobachteter `Chat voll`-Share-Zeitfenster-Workaround ausdrücklich als nicht garantiert dokumentiert
- alle v1.6.0-Sprach-, v1.5.x-Backend-, Bildbrowser- und Bootstrap-Funktionen erhalten

## 1.6.0 — 2026-10-20

- English als Standard-Sprache für neue Installationen eingeführt.
- Persistente Sprachwahl `language=en|de` in `settings.json`.
- Neuer Menüpunkt `Language / Sprache` links in der Hauptnavigation.
- Sofortige Umschaltung der Hauptoberfläche zwischen English und Deutsch.
- Neuer Menüpunkt `Help / Hilfe` mit vollständiger Bedienungsanleitung in beiden Sprachen.
- Sprachabhängige Hauptnavigation, Link-/Editor-Bereiche, Einstellungen, Struktur-Inspector, Bildbrowser, Status-/Dialogtexte und About-Dialog erweitert.
- Bestehende Chat-Backend-, Struktur-JSON-, Raw-Source-, Bildbrowser- und Portable-Backup-Funktionen unverändert erhalten.
- Windows PowerShell 5.1 Bootstrap-Härtung aus v1.5.2 unverändert erhalten.

# CHANGELOG

## 1.5.2 — 2026-10-19

- Struktur-Inspector kann die aktuell ausgewählte Nachricht als eigenständiges JSON speichern
- Struktur-Inspector kann die komplette sichtbare/strukturierte Chatansicht als `*_STRUCTURE_INSPECTOR.json` speichern
- stabiles Schema `666.chatbackup.structure-inspector.v1` eingeführt
- Inspector-JSON enthält Parser-Zusammenfassung, Integritätsprofil, Parser-Provenienz, Raw Content/Metadata, Copy-Felder, Warnungen, Assets und gerenderten Text
- Portable-ZIP enthält zusätzlich `source/structure_inspector.json` samt SHA-256 im Manifest
- bytegenauer Readback wird auch für die neuen Inspector-JSON-Dateien verwendet
- v1.5.0 Backend-, Bildbrowser-, Raw-Source-, Reparse- und Maschinenexport-Funktionen bleiben erhalten

## 1.5.0 — 2026-10-19

- neues `ChatBackend` als eigenständige Orchestrator-Schicht
- Message-ID, Content-Type, Status, Recipient, Raw Content und Raw Metadata werden erhalten
- statische `GenUI.copy(identifier)`-Analyse ohne `eval`
- Copy-/UI-Felder mit resolved/unresolved und UTF-16-Länge
- Parser-Provenienz und Primärfehler
- Raw-Share-Source-Capture mit SHA-256 und Reparse-API
- Struktur-Inspector in der GUI
- Maschinenexport-Schema auf `1.2.0` erweitert
- Portable-ZIP um `source/conversation.raw.json`, `source/parser_receipt.json` und optional `source/share-source.html.gz` erweitert
- mehrdimensionale Integritätssemantik statt einfachem PASS
- v1.4.0 Bildbrowser, selektiver Bildexport, Bootstrap und Long-Chat-Repair vollständig erhalten

# Changelog

## 1.4.0 — 2026-10-10

- echter Chat-Bildbrowser als scrollbare Galerie hinzugefügt
- Vorschaubilder/Thumbnails für direkt erreichbare Chat-Bilder
- Großansicht und Original-im-Browser-Funktion
- Auswahl pro Chat-Bild über Checkbox
- Massenauswahl: alle / keine / nur direkt erreichbare
- Portable-ZIP speichert nur ausgewählte Chat-Bilder
- abgewählte Bilder werden als `SKIPPED_BY_USER` protokolliert
- stabile `assetKey`-Kennung und `selectedForPortable` im Maschinenexport
- `assetSelection` im JSON/JSONL ergänzt
- konservative Auflösung pointergebundener Bilder über eingebettete Share-Asset-Tokens
- Pillow als automatisch verwaltete Runtime-Abhängigkeit für PNG/JPEG/WebP/GIF/BMP-Vorschauen
- optionales automatisches Öffnen des Chat-Bildbrowsers nach Link-Laden
- lokale Bilder als sekundärer Zusatzworkflow beibehalten
- alle v1.3.0-, v1.2.1- und Long-Chat-Reparaturen erhalten

## 1.3.0

- Maschinen-JSON und JSONL
- Portable ZIP mit Bildintegration
- Neon-Pink-Titel und Cyber-Neon-GUI

## 1.2.1

- Windows-PowerShell-5.1-Encoding/BOM-Reparatur

## 1.1.1

- bytegenauer Long-Chat-Readback
## v1.5.2 — Windows Bootstrap Patch-Update Hardening

- Python-Patchupdates bei bereits kompatibler Runtime sind jetzt best-effort und blockieren den App-Start nicht.
- python.org-Verzeichnisse werden nicht mehr automatisch als vorhandene Windows-Binaerinstaller interpretiert.
- Neue installer-aware Erkennung prueft, ob der passende Windows-Installer tatsaechlich erreichbar ist.
- Source-only Python-Security-Releases koennen damit keinen 404-Fehlversuch mehr als vermeintlich erforderliches Update ausloesen.
- winget bleibt bevorzugter Updateweg; Fehlschlag faellt sicher auf die vorhandene kompatible Runtime zurueck.
- Pflichtinstallation bei fehlendem/zu altem Python und Tkinter-Reparatur verwenden ebenfalls nur nachgewiesen verfuegbare Windows-Installer.


## v1.10.3 — 2026-11-06

- PC runtime architecture preserved from v1.10.0.
- Bundled Scriptable companion updated from v1.0.0 to v1.0.6.
- Previous mobile companion preserved under `mobile_scriptable/history/`.
- Added variant-tolerant Scriptable SSR/React-Flight integration evidence.
- Added package-level mobile byte-equality/readback verification.
