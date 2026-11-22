# Status: R13 + Windows-Abnahmeunterlagen

- R13-Kern: unverändert; **nicht** auf neue Versionsnummer umetikettiert.
- HDDLEDPRO.exe/Victoria.exe: SHA-256/PE-Header geprüft, **nicht ausgeführt** oder beigepackt.
- HDDLEDPRO.ini: Einstellungen gelesen, weder Semantik der Intervall-Einheit noch Kompatibilität mit R13 behauptet.
- Victoria.ini: lokale Diagnose-Konfiguration; sensible Felder werden nicht weitergegeben.
- Automatisierte Regression des übernommenen R13-Basisprojekts: siehe `REGRESSION_RESULT.json`.
- Echter Tray-/Mehrmonitor-/Lock-Test unter Windows: `READBACK_PENDING`.
- **Nicht als VERIFIZIERT ausgeben**, bis Windows-Bericht und ggf. unabhängige Evidenz vorliegen.
