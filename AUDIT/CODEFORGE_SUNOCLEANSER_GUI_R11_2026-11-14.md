# CodeForge R11 · SunoCleanser GUI-Ausgabeordner

Basis: `01328cf798c1c6a94d1e6653e21d93dbd34e3d82`

Wenn der Dateimanager-Aufruf beim Öffnen des Ausgabeordners einen `OSError` auslöste, erreichte der Callback den vorhandenen Pfad-Hinweis nicht. Der Fehler wurde vor der Änderung durch einen `FileNotFoundError` im Launcher reproduziert. Der Patch behandelt Betriebssystemfehler des Launchers und nutzt den vorhandenen lokalisierten Ordnerdialog. Erfolgreiche Aufrufe, Pfade und DSP bleiben erhalten.

| Prüfung | Ergebnis |
|---|---|
| Ruff 0.17.5 und Pyright 1.1.414 | PASS im Projektpfad vom Repository-Root aus. |
| pytest mit den sechs Frozen-Lock-Abhängigkeiten | 29/29 PASS, darunter fünf neue Fälle für fehlende Launcher unter Linux, macOS und Windows sowie Exit 0 und Exit 1. |
| SHA256SUMS | Vollständiger Readback der eingetragenen Dateien PASS. |

Die GUI-Regressionen verwenden Test-Doubles für Launcher und Dialog. Der Lauf erfolgte lokal unter Linux ohne interaktiven Windows-Host. Die Windows-GUI-, Fresh-Chat- und UCA-Host-Abnahmen stehen weiter aus. Die GitHub-Actions-Abfrage für den Branch lieferte keine Runs.
