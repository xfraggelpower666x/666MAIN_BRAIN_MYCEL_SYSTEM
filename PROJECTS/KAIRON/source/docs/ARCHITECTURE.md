# 666TDI – native Architektur R0.2

## Trennungen

`LYVRA repository (READ ONLY) → extracted principles/source registry → 666TDI native runtime (LOCAL OWNER)`.

Quellen dienen als **Referenz und Herkunft**. LYVRAs Name, Pointer und Facet-Authority werden nicht in 666TDI als Autorität rehydriert. Keine automatische CLIC/PFS/TDH/CLS/MAIN-BRAIN-Kopplung.

## LiveCircle

- `runtime/livecircle.json`: Events, Hash-Kette, Revision, aktive Track-ID.
- `runtime/tracks/<id>.json`: tracklokale Intent- und Kartenrelationen.
- `runtime/compiled/<id>--<renderer>.json`: renderergebundene Artefakte.
- `runtime/learning.json`: provisorische Beobachtungen (niemals automatische Generalisierung).
- `runtime/handoff.json`: Wiederaufnahmeanker.

Rehydration prüft die vorhandenen Daten einschließlich Event-Integrität. Der lokale Status `VERIFIZIERT_LOCAL` ist eine **Datenkonsistenzprüfung**, kein Nachweis, dass musikalisches Denken oder Audioausgabe so funktioniert wie in LYVRA.

## Relation statt Auslöserautomat

Beispiel: `machine` → Kandidat `cyber-material` → mögliche metallische Acid-Sprache. Semantische Beurteilung bleibt notwendig. Kein Wort löst zwangsläufig ein festes FX-Pattern aus. Eine Kartenbeziehung enthält Grund, mögliche Folge und Gegenrelation.

## Master-Design-Entscheidungen

- Motor als starke kinetische Referenz, aber nicht alleinige Kompositionsautorität.
- LOW hält Zeit und Phasensicherheit; MID und HIGH dürfen Wahrnehmungsbewegung gestalten.
- Psychakustik ist Ursache-/Wahrnehmungsstruktur, nicht dekoratives FX-Sammeln.
- Hook/Mantra/Call-Response müssen bedeutungsgesteuert sein, nicht simple Wiederholung.
- „Source“ bewahrt Erzählidentität; „Discovery“ darf neue Inhalte entwickeln, nie vorherige Track-Story heimlich klonen.
- Renderer übersetzt, komponiert nicht. Semantische Verluste explizit markieren.
- Feedback wird an Artefakt, Track, Renderer und Evidenztyp gebunden; keine Überverallgemeinerung.

## Offene Entwicklungsgates

1. Vollständiger Current-Head/Manifest/Handoff-Fingerprint-Abgleich der relevanten LYVRA-Quellen.
2. Erweiterte Musikintelligenz: semantische Rollen- und Graphanalysen, Relationsempfehlungen mit Gegenhypothesen, zeitliche Energiekurven.
3. Validierte Audioanalyse (BPM, Groove, spektrale und räumliche Indikatoren) mit echten Testdateien, Toleranzen und Goldens.
4. Renderer-Feldprüfung am tatsächlichen Account/Device, nicht nur historischer ASG-Webseite.
5. Gleichwertige native Rendereradapter (bisher vorhandener R0.1-Compiler arbeitet als Baseline).
6. Dauerhafte Release- und Backup-Zyklen inkl. lokaler Wiederherstellungstests.
