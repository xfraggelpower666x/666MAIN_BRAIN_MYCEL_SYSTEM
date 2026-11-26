# R01.4 CYBER BOOT — additive Entwicklung

- Grundlage: R01.3 ZIP, kein neues Projekt.
- `STARTEN.bat` startet weiterhin `STARTEN.ps1` mit prozessbezogener PowerShell-Ausführungsrichtlinie.
- Neues `tools/cyber-boot.ps1`: bildschirmfüllende Intro-Ansicht mit exakt dem gelieferten Cyber-Boot-Motiv; letterbox/contain ohne Verzerrung; echte, schreibgeschützte Werkzeugerkennung; Fortschritt aus sechs tatsächlich abgeschlossenen Statusschritten; ESC überspringt das Intro. Kein automatisches Update/Installation beim Boot.
- Das im Motiv eingebrannte Beispiel `78%` und die Status-Häkchen werden zur Laufzeit durch ein dynamisches Panel abgedeckt, damit kein gefälschter Prüfstatus als real angezeigt wird.
- Das Menü wurde vom überdeckenden Bild-Banner befreit; alle 8 Aktionsbuttons sind wieder unmittelbar sichtbar.
- `STARTEN.bat menu` behält den Konsolenmodus; alle bisherigen Aktionstypen bleiben unverändert.
- Build-/Installationslogik wurde nicht verändert.
- Windows 10/11 + Windows PowerShell 5.1 / WinForms für die Boot-Ansicht erforderlich.
- Windows-GUI- und Windows-Build-Abnahme stehen aus; lokale Python-Tests sind keine Windows-Ausführungsfreigabe.
