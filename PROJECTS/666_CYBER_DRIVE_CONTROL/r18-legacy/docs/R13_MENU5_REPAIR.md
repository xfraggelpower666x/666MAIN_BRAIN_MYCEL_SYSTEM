# R13 MENU-5 — Reparatur der Python-Erkennung

Basis: R13 MENU-4. Erhalten: alle Python-Quellmodule und Funktionen; nur Tool-Manager, Batch-Beschriftung und Tests ergaenzt.

## Befunde

- M5-01: `Find-Python` verwarf jeden `WindowsApps`-Kandidaten aufgrund des Pfadnamens. Dadurch konnten echte Python-Manager-Launcher nicht einmal getestet werden. Reparatur: Kandidaten auch dort zulaessig, aber ausnahmslos auf ausfuehrbaren Python >=3.10 pruefen. Der nicht funktionsfaehige Store-Alias faellt weiterhin beim Versions-/Exit-Test durch.
- M5-02: Python auf nicht standardisierten Laufwerken war nicht manuell auswählbar. Reparatur: Bei Menuepunkt 2 nach erfolgloser automatischer Suche optional Eingabe eines vorhandenen `python.exe`-Pfads; eine Installation ist weiterhin nur nach expliziter Zustimmung moeglich.
- M5-03: Bisher gab es keine Liste getesteter Python-Pfade. Reparatur: `python_candidates` mit Pfad, Argumenten, Erfolg und Version im Tool-JSON; keine sensiblen Daten separat ausgeben.

## Grenzen

- Nur Python-Syntax-/Text- und Linux-Regression getestet. Windows-PowerShell-5.1-Hostpruefung, winget-Installationslauf und echte Tray-Anzeige bleiben READBACK_PENDING.
- Erkanntes Python allein bedeutet nicht READY: lokale .venv und Abhaengigkeiten muessen in Menuepunkt 2 eingerichtet werden.
