# R01.9 — Cyber-Boot HUD / Encoding Repair

Quelle: vollständiges R01.8 ZIP. Keine Änderung an Buildfunktionen oder Timings.

- Neon-Rahmen/Statusfeld wird einmalig in die Boot-Artwork-Kopie komponiert. Die Original-Artwork bleibt als `cyber-boot-artwork-original.png` erhalten.
- Transparentes WinForms-Panel hält nur die dynamischen Statuslabels und den zeitbasierten Balken. Kein blockartiger dunkler Overlay-Hintergrund.
- Zustandsindikatoren sind `OK` / `!` / `--` in ASCII und damit unabhängig von Windows PowerShell 5.1 Unicode-Interpretation.
- 8-Sekunden-Laufzeit, Meilensteine, ESC, Buildfunktionalität und Launch-Verkabelung bleiben unverändert.
- Prüfungen sind read-only; `OK` beim Boot bedeutet nur eine erfolgreiche kurze Pfad-/Bootprüfung, nicht validierten Build.
- Lokale Quelltests ohne Windows-GUI. WinForms-Pixel- und Verhaltenstest unter Windows weiterhin offen.
