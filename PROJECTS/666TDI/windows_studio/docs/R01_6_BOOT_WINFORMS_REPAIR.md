# R01.6 — Windows WinForms Cyber-Boot Repair

## Reproduzierbarer Ausgangsfehler

Windows PowerShell 5.1 meldet beim Start des `tools/cyber-boot.ps1`:
`Die Eigenschaft "DoubleBuffered" wurde für dieses Objekt nicht gefunden`.
Der Fehler wird in `STARTEN.ps1` abgefangen; dadurch folgt der Fallback auf das Control Center.

## Minimalinvasiver Patch

In `tools/cyber-boot.ps1` wurde ausschließlich die unzulässige Zuweisung
`$form.DoubleBuffered = $true` entfernt. `DoubleBuffered` ist auf
`System.Windows.Forms.Form` nicht öffentlich beschreibbar. Die bestehende
WinForms-Paint-Routine, die 8-Sekunden-Meilensteine, die Bildassets, ESC,
Statusprüfungen und die Build-Aktionen bleiben erhalten.

Der Fenstertitel im Menü wurde von R01.4 auf R01.6 aktualisiert.
Ein Regressionstest sichert das Fehlen dieser fehlerhaften Zuweisung.

## Grenzen

Die Windows-WinForms-GUI wurde nicht auf einem Windows-Host ausgeführt.
Die lokalen Python-Tests prüfen Quellverträge, keine echte GUI-Laufzeit.
Bitte `STARTEN.bat` auf Windows ausführen und den vollständigen
achtsekündigen Bootscreen plus Menüübergang abnehmen.
