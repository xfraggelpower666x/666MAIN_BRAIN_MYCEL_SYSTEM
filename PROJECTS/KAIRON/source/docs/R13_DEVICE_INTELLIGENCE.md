# 666TDI R1.3 – Device Intelligence

## Quellordnung
TDI-Authority: produktiver Branch `666MAIN_BRAIN`; musikalische R0.9–R1.2-Entscheidungen bleiben unverändert. Die LYVRA-Referenz `LYVRA_NATIVE_RUNTIME/current/music/TRACK_DESIGN_IPHONE_CUSTOM_THREE_ROUTES_20261029.md` wurde auf Branch `lyvra` ausschließlich lesend geprüft. Creator-beobachtete Workflows sind nicht automatisch aktuell unabhängig vom Suno-Provider verifiziert.

## Implementiert
- Drei Routen für zwei Geräte: `IPHONE_CUSTOM_NO_MAIN`, `IPHONE_CUSTOM_WITH_MAIN`, `PC_BROWSER`.
- iPhone Main Input ausschließlich mit explizitem Opt-in und Creator-Text; ausdrücklich leeres Main bleibt leer.
- PC Duration-Slider wird nur bei expliziter Sichtbarkeitsbestätigung berücksichtigt. PC Main Input und iPhone-Slider werden nicht erfunden.
- Vier Basisfelder: Title, Extended, Style, Lyrics. Das Exclude/Avoid-Textmaterial fließt in Extended, kein separates erfundenes Exclude-Feld.
- Exakte UTF-16-Zählung einschließlich Emojis und Newlines, Referenzbudgets 80/1000/1000/5000 (aus Creator-Workflow, nicht unabhängig provider-verifiziert). Überlange Felder werden sichtbar markiert, nicht stillschweigend verkürzt.
- Copy-Buttons kopieren genau den sichtbaren, lokal bearbeiteten Text; für leere oder über Referenzbudget liegende Felder gesperrt.
- JSON-Handoff enthält Copy-Felder und Creator-Entscheidungen; kein Suno-Render und kein GitHub-Write durch den Daemon.

## Technische Grenzen
Die Geräte-Übersetzung verwendet ausschließlich vorhandenen Creator-Text, nicht neue kompositorische Aussagen. R1.0-R1.2 bleiben geräteunabhängig. Die Felder sind Source-Projektionen und keine Behauptung automatisch fertiger Suno-Tracks. Keine Live-Suno-Oberflächenverifikation, keine Suno-API, kein tatsächliches Audio, keine fremde Authority, keine automatische globale Lernregel.

## Dateien
`source/engine/device_output.py` – Ausgabeadapter.
`source/engine/daemon_cli.py` – R1.3-API-Integration.
`source/engine/daemon_static/index.html` – Routenauswahl und Copy-Felder.
`source/tests/test_device_output.py` – gerätebezogene Regressionen.

## Start
Im Verzeichnis `source`: `python -m engine.daemon_cli --port 8766`, danach `http://127.0.0.1:8766` öffnen.

## Offene Abnahmen
Python-Lauf und Host-Browser-Kopie sind in diesem Veröffentlichungsprozess nicht ausgeführt. Eine neue aktuelle Suno-Control-Oberfläche muss vor einer späteren Provider-spezifischen Erweiterung gesondert geprüft werden.
