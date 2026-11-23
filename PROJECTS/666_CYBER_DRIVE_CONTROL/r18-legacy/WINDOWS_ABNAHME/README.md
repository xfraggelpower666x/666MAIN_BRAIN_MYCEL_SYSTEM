# R13 — Windows-Abnahme / Readback

**Keine vollständige Windows-Abnahme im Linux-Build.** Das Paket enthält die unveränderte R13-App plus einen lokalen Prüfablauf für Windows 10/11. Kein automatischer Treiber- oder Firmwarezugriff und keine Ausführung der hochgeladenen Drittanbieter-EXE.

## Durchführung

1. Entpacke das vollständige ZIP. In PowerShell im Projektverzeichnis: `py -m pip install -e ".[tray]"`.
2. Starte `WINDOWS_ABNAHME/START_WINDOWS_READBACK.bat` oder `powershell -NoProfile -File .\WINDOWS_ABNAHME\RUN_WINDOWS_READBACK.ps1`.
3. Prüfe das Tray-Symbol, das Show/Hide-Menü, Lock-Tasten Num/Caps/Scroll in beiden Zuständen, SSD Read/Write, Netzwerk RX/TX, RGB-Auswahl, Mehrmonitorbetrieb und Beenden.
4. Der **JSON-Prüfbericht** liegt unter `WINDOWS_ABNAHME/REPORTS/R13_WINDOWS_READBACK_*.json`. Teilen, um Probleme anhand echter Windows-Evidenz minimalinvasiv zu beheben.

`-PreviewOnly` prüft Python, optionale Abhängigkeiten und Bildschirme, ohne das Tray zu starten. `MANUAL_CHECKS_REPORTED_PASS` ist **eine Selbstauskunft**, nicht eine unabhängig verifizierte Hardwareabnahme. Bei Importfehlern: `py -m pip install -e ".[tray]"` im Projektordner. Beim Lock-Test nicht unabsichtlich Schreib-/Arbeitsabläufe mit aktiven Caps-/Num-Locks verändern.

## Nachweislücken

Die Sichtbarkeit des Tray-Symbols lässt sich aus Prozess-Lebendigkeit allein nicht beweisen; die Bildschirmliste ist kein Nachweis für korrekte Fensterpositionierung; `GetKeyState` in einer GUI kann je nach Windows-Thread/Fokus einen veralteten Zustand liefern. Deshalb sind echte Bedien- und Fokuswechsel-Tests erforderlich. Eine erhöhte Genauigkeit des Disk-Monitors gegenüber HDDLEDPRO ist nicht gemessen.
