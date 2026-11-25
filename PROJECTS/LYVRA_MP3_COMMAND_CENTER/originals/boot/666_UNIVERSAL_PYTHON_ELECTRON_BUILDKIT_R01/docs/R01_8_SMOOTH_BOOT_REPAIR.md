# R01.8 — Smooth Cyber Boot Repair

- Ausgangsbefund: R01.7 zeichnet das vollstaendige Hintergrundbild bei jedem Statuswechsel mit `DrawImage` und `Invalidate` neu; Balken berechnet Prozent nur aus `step/6`.
- Reparatur: separates statisches `PictureBox` mit `Zoom`, deckendes Statuspanel als Child, WinForms-Timer (33 ms), zeitbasierte Prozentanzeige `elapsed/8000`, Statusphasen bei 950/2150/3350/4550/5850/7200 ms.
- Boot bleibt read-only, bestaetigte Tool-Funde erhalten eigene Kennzeichnung. Read-only Scan ist keine Build-Abnahme.
- Die bisherige Start-BAT, Menue, Electron und Buildwerkzeuge sind unveraendert.
- Laufzeit-Windows-GUI-Test steht aus. Lokale Tests sind statische Regression und Python-Funktionstest, kein Nachweis fuer Windows-GPU/Compositor-Leistung.
