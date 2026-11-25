# R07 – Electron Neon Control UI (local candidate)

Basis: bestehendes R06.1 funktionierendes AUTO-DJ Studio. Source branch `666MAIN_BRAIN`, geprüfter HEAD `f3d3b7d54e3e7f2ef990c25ea181890ae7e85a0f`.

Änderungen ausschließlich in `app/index.html`, `app/theme.css`, `app/renderer.js`, `app/main.js`, `app/preload.js`. Track-Liste mit Entfernung einzelner Dateien, Fortschrittsbalken, Live-Status, aufgeteilte Engine-/Cover-/Exportbereiche, sichere Cover-Vorschau einer Bilddatei aus einem gewählten Ordner. Bereits bestehende Audio- und Exportparameter bleiben unverändert. Cover-Vorschau ist lesend und ändert NICHT den FFmpeg-Cover-Rotationsalgorithmus.

Keine Änderungen an `legacy/tool.ps1`, `engine/`, `BUILD.bat`, `build/` oder `package.json`. Kein GitHub-Write/Current-Pointer-Update.

Akzeptanz offen: tatsächlicher Windows-Electron-Start dieser UI-Revision, Cover-Vorschau mit echten Dateien, Audio-E2E, Portable/NSIS.

Hinweis: Originale 29 Covers, FFmpeg und FFprobe sind Bestandteil dieser vollständigen lokalen ZIP-Lieferung; im GitHub-Quellbaum sind sie noch nicht vollständig veröffentlicht.
