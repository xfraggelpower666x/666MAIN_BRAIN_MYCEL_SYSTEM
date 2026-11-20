# 666 ChatBackup PC Tool v1.10.5

Windows-Desktoptool zum Archivieren öffentlicher ChatGPT-Share-Chats sowie privater/manuell kopierter Einzel- und Gruppenverläufe. Englisch ist Standard; die gewählte Sprache bleibt persistent.

Current authority: `CURRENT_RELEASE_INDEX.md`

## Neu in v1.10.5

- PC-Import für SSR-Transkripte mit `data-message-role`, HTML-ID und direkten Bildreferenzen.
- Windows-Abnahme prüft `app/chatbackup_gui.pyw` samt Browser-Recovery-Dialog mit demselben Python für alle Prüfschritte.
- Release-Prüfung verifiziert die Dateien des PC-Manifests und den eingebetteten Companion.
- Scriptable v1.0.9 führt Host-Abnahme und Menüimport über dieselbe Fallback-Kette aus.

## Entwicklung in v1.10.4 — Full Host Acceptance & Scriptable v1.0.8

v1.10.4 verändert den funktionierenden PC-Importkern bewusst nicht unnötig. Der Release synchronisiert den mobilen Companion und macht die zwei verbleibenden Host-Gates reproduzierbar prüfbar.

- aktueller eingebetteter iPhone-Companion: **666 ChatBackup Scriptable iPhone v1.0.8**
- alter v1.0.6-Companion bleibt unter `mobile_scriptable/history/` erhalten
- bytegleiche Companion-ZIP zwischen Standalone- und PC-Paket
- Scriptable v1.0.8: Variantentoleranz für React-Flight + SSR-Transcript, On-Device-Selbsttest und Share-Kompatibilitätsprobe
- bestehender Windows-Runtime-Probe bleibt erhalten
- neuer Gesamt-Hosttest `VERIFY_WINDOWS_HOST_ACCEPTANCE.bat`
- neuer End-to-End-Probe `tests/host_acceptance_probe.py` für Live-Share Fetch → Parse → Export → Readback
- Windows-Probe liest echte Core-/Backend-/Tkinter-/Pillow-/GUI-Initialisierung, Fenstertitel und Geometrie zurück
- ein Nicht-Windows/Xvfb-PASS validiert nur den Probe-Code und schließt den Windows-Host-Gate ausdrücklich **nicht**

## Erhalten aus v1.10.0 — AUTH-Wall & Browser Recovery

- `AUTH_WALL_DETECTED` als eigener Zustand statt irreführendem Parserfehler
- Direktparser bleibt Stufe 1
- Browser-Recovery nur bei fehlendem Conversation-Payload
- keine Cookie-Extraktion, kein Login-Bypass, keine Credential-Nutzung
- fail-closed Clipboard-Rekonstruktion
- keine erfundenen Bild-/Dateibytes

## iPhone / Scriptable Companion

Current ist `mobile_scriptable/666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.9.zip`.

Der Companion besitzt jetzt unter **Diagnostics / Self-Test**:

- Offline-Selbsttest mit 7 Prüfungen
- Public-Share-Probe ohne Backup-Erzeugung
- **Run host acceptance** für Live-Share Fetch → Parse → Export → FileManager-Readback
- Source-Fingerprint für Flight/Legacy/SSR
- maschinenlesbare JSON-Berichte/Receipts für echten iPhone-Readback

Historische Companion-ZIPs bleiben unter `mobile_scriptable/history/` erhalten.

## Host-Readback / Abnahme

### Windows

`VERIFY_WINDOWS_HOST_ACCEPTANCE.bat` ausführen und einen echten öffentlichen ChatGPT-Share-Link angeben. Nur `WINDOWS_HOST_ACCEPTANCE_PASS` aus dem realen Windows-Host schließt den Windows-Gate.

### iPhone

Im Scriptable-Companion `Diagnostics / Self-Test` → `Run host acceptance` mit einem echten öffentlichen Share-Link ausführen. Nur `HOST_ACCEPTANCE_PASS` auf dem realen iPhone schließt Runtime + realen Share-Import/Export-Gate.

## Neu in v1.8.2 — Direkter Bilddownload im Chat-Bildbrowser

- jedes direkt erreichbare Chat-Bild hat jetzt einen eigenen **Download**-Button
- **Ausgewählte herunterladen / Download Selected** speichert alle angehakten direkt erreichbaren Bilder in einen gewählten Ordner
- **Alle erreichbaren herunterladen / Download All Reachable** speichert alle abrufbaren Chat-Bilder gemeinsam
- Download ist auch aus der Großansicht möglich
- gespeicherte Bilddateien werden bytegenau zurückgelesen und SHA-256-verifiziert, wenn Export-Verifikation aktiv ist
- Portable ZIP speichert Bildbytes als echte Binärdateien unter `assets/`, **nicht als Base64**
- Pointer-only-Bilder ohne erreichbare HTTP(S)-URL bleiben als Metadaten erhalten und können nicht erfunden werden

## Neu in v1.8.1 — Audit, Repair & Group-Chat Hardening

- vollständiger Versionskohärenz-Repair: App, VERSION.json, Bootstrap-Status und Abhängigkeitsmanifest melden jetzt denselben Stand
- strukturierte Assistant-/Custom-GPT-Identitäten werden nicht mehr pauschal zu `ChatGPT` zusammengezogen
- Teilnehmerverzeichnisse werden primär nach stabiler ID dedupliziert
- generische Rollenplatzhalter wie `user` / `assistant` werden nicht als Personennamen übernommen
- manueller Gruppenchat-Parser gegen falsche Sprecher aus normalen Markdown-Überschriften gehärtet
- `## Alice`-Sprecherüberschriften bleiben für exportierte Transcripts unterstützt, wenn sie an Transcript-Grenzen (`---`) stehen
- neue Regressionstests für Heading-False-Positives, Assistant-Identität und Versionskohärenz
- bestehende v1.8.0-Gruppenchat-, v1.7.0-Manual-, v1.6.0-Sprach-, Bildbrowser- und Raw-Source-Funktionen bleiben erhalten

## Gruppenchat / Mehrteilnehmer

- strukturierte Share-Daten: explizite Teilnehmer-IDs, Anzeigenamen und Benutzernamen werden pro Nachricht erhalten
- manuelle Transcripts: eindeutige `Name:`-Sprecherzeilen werden erkannt; Markdown-Sprecherüberschriften nur an klaren Transcript-Grenzen
- Machine JSON `666.chatbackup.machine.v1 / 1.3.0` und Structure Inspector `1.1.0` führen Teilnehmerinformationen weiter
- fehlende Identität bleibt `UNRESOLVED`; es wird nicht anhand von Stil oder Reihenfolge geraten

## Neu in v1.5.0 — ChatBackend

- eigener Backend-Orchestrator `app/chatbackup_backend.py`
- verlustarme Message-Struktur mit ID, Content-Type, Status, Recipient, `rawContent`, `rawMetadata`, `renderedText`, Warnungen und Assets
- statische Erkennung von `GenUI.copy(identifier)` und zugehörigen literalen `const`/`let`-Strings
- keine Ausführung von Chat-JavaScript; dynamische Templates bleiben ungelöst
- Parser-Provenienz mit Versuchsliste und Primärfehler
- Raw-Share-Source-Capture mit SHA-256 und 12-Millionen-Zeichen-Grenze
- Reparse-API für archiviertes Share-HTML
- neuer Struktur-Inspector in der GUI
- Maschinenexport-Schema `1.2.0`
- Portable-ZIP erhält `source/conversation.raw.json`, `source/parser_receipt.json` und optional `source/share-source.html.gz`
- Integritätsstatus trennt Quelle, Raw-Erhalt, UI-Bindungen, Assets und visuelle Parität

## Erhalten aus v1.4.0

- Cyber-Neon-GUI in Pink/Lila/Cyan
- große adaptive Fenstergröße und Neon-Hover
- Fortschrittsbalken bei großen Einfügevorgängen
- Share-Link-Parser: React Flight, `__NEXT_DATA__`, statischer DOM-Fallback
- Chat-Bildbrowser mit Auswahl pro Bild
- Asset-Pointer-Erhaltung und konservative URL-Anreicherung
- TXT, Markdown, JavaScript, JSON, JSONL
- Portable ZIP mit ausgewählten Bildern
- bytegenauer Export-Readback / SHA-256
- PowerShell-5.1-sicherer Bootstrap
- Node.js / NPM weiterhin `NOT_REQUIRED`

## Start

Unter Windows den Ordner vollständig entpacken und `START_TOOL.bat` starten. Der Bootstrap prüft Python, Tkinter und Pillow für den Quellstart. Eine gebaute Standalone-EXE bringt ihre Python-Laufzeit mit.

## Struktur-Inspector

Nach einem Share-Import über `Struktur-Inspector` erreichbar. Er zeigt pro Nachricht u. a. Message-ID, Rolle, Content-Type, Raw Content, Raw Metadata, Copy-/UI-Felder, Warnungen und gerenderten Text.

## Raw Source

In den Einstellungen ist `Original-Share-Quelldaten für Reparse/Archiv erhalten` standardmäßig aktiv. Die HTML-Quelle wird nicht als sichtbarer Export ausgegeben, sondern für das Portable-Archiv komprimiert gespeichert. Bei mehr als 12.000.000 Zeichen wird nicht still abgeschnitten, sondern der Status `RAW_TOO_LARGE_NOT_STORED` gesetzt.

## Exportformate

- TXT — Editorinhalt
- MD — lesbares Markdown mit Integritätssektion und erkannten Copy-Feldern
- JS — sicher serialisiertes Exportobjekt
- JSON — Maschinenformat `666.chatbackup.machine.v1 / 1.3.0`
- JSONL — streambares Maschinenformat
- Portable ZIP + Bilder — alle Formate, Assets und Source-/Parser-Artefakte

## Grenzen

- Öffentliche `/share/`- bzw. `/s/`-Links sind ohne Anmeldung direkt auslesbar.
- Private `/c/`-Links werden nicht authentifizierungsfrei geladen; dafür steht der strukturierte manuelle Import zur Verfügung.
- Dynamische UI-Logik wird nicht ausgeführt.
- Ein Parser-PASS ist ausdrücklich kein Nachweis pixelgenauer UI-Rekonstruktion.
- Nicht öffentlich gelieferte Bildbytes können nicht erfunden werden; Asset-Pointer bleiben aber maschinenlesbar erhalten.
- Eine echte Windows-EXE muss unter Windows gebaut und dort verifiziert werden.

## Neu in v1.5.2: Struktur-Inspector als JSON

Der Struktur-Inspector ist jetzt nicht nur eine Ansicht. Über **Nachricht JSON** lässt sich die aktuell markierte Nachricht exakt strukturiert speichern; **Komplette Struktur JSON** speichert den gesamten Inspector-Snapshot. Das stabile Schema heißt `666.chatbackup.structure-inspector.v1`. Portable ZIPs enthalten denselben Gesamtsnapshot zusätzlich als `source/structure_inspector.json`.


## Neu in v1.8.0 — Gruppenchat- / Mehrteilnehmer-Backend

- explizite Teilnehmer-IDs, Anzeigenamen und Benutzernamen aus strukturierten Share-Daten bleiben erhalten
- automatische Gruppenchat-Erkennung nur anhand expliziter Metadaten oder mindestens zweier explizit unterscheidbarer menschlicher Teilnehmer
- manuelle Gruppenverläufe mit eindeutigen Sprecherzeilen wie `Alice:`, `Bob:`, `ChatGPT:` werden strukturiert rekonstruiert
- keine Identität wird geraten; fehlende Zuordnung bleibt `UNRESOLVED`
- Machine JSON/JSONL, Raw Source und Structure Inspector enthalten Teilnehmerverzeichnis und Teilnehmerbezug je Nachricht
- Machine-Schema `666.chatbackup.machine.v1` jetzt `schemaVersion=1.3.0`
- Structure-Inspector-Schema jetzt `schemaVersion=1.1.0`

Hinweis: Die Funktion dient auch zur Archivierung bestehender/älterer Gruppenchat-Verläufe. Wenn ChatGPT keinen öffentlichen Share-Link anbietet, kann der sichtbare Verlauf über den Private-/Manual-Workflow importiert werden.

## Release integrity readback

Run `VERIFY_RELEASE_INTEGRITY.bat` to verify the PC manifest and the embedded Scriptable ZIP, SHA-256, mobile version/manifest and Current-vs-History mapping without Pytest. The result is written to `runtime_readback/release_integrity_readback.json`.
