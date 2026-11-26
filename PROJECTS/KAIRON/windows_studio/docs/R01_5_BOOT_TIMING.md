# R01.5 — Cyber-Boot Timing (8 Sekunden)

Additive Fortsetzung auf Basis von R01.4. Der vorhandene Bootscreen und das GUI bleiben erhalten.

| Bootphase | Einblendung ab | Bedeutung |
| --- | ---: | --- |
| INITIALIZING SYSTEM | 0,95 s | Oberfläche gestartet |
| SCANNING TOOL PATHS | 2,15 s | Pfadscan initialisiert |
| CHECKING PYTHON | 3,35 s | Python aufrufbar? |
| CHECKING GIT | 4,55 s | Git aufrufbar? |
| CHECKING NODE / ELECTRON | 5,85 s | Node vorhanden? lokaler Electron-Ordner? |
| BUILD ENVIRONMENT SCANNED | 7,20 s | Read-only-Prüfungen abgeschlossen, nicht alle Werkzeuge notwendigerweise vorhanden |
| Übergang ins Menü | 8,00 s | Abschlussphase bleibt 0,8 s sichtbar |

Die Statusanzeige zeigt nur reale Prüfergebnisse; fehlende Tools werden nicht als OK ausgegeben. Der Timer verwendet eine Stopwatch, kein aufaddiertes Tick-Zählen. Auf langsamem Rechner können Prüfungen den Zeitrahmen verlängern, weil sie synchron laufen. ESC überspringt jederzeit das Intro. Keine Installation beim Intro. Windows-WinForms-Abnahme offen.
