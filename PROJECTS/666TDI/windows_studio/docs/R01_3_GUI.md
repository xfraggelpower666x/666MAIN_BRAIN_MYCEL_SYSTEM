# R01.3 GUI additive Erweiterung

- STARTEN.bat startet Windows PowerShell 5.1 im STA-Modus.
- STARTEN.ps1 öffnet standardmäßig die WinForms-Oberfläche; `STARTEN.bat menu` ruft weiterhin die alte Konsolenoberfläche auf.
- Acht Schaltflächen leiten exakt die vorhandenen Build-Engine-Aktionen weiter. Keine neue Installationslogik.
- Original-Bootscreen wird im GUI-Header proportional dargestellt.
- Build-/Installationsaktionen erhalten eigene, sichtbare PowerShell-Fenster für bisherige interaktive Freigaben.
- Es erfolgt kein automatisches Update oder Installieren beim Öffnen des Menüs.
- Einschränkung: Windows PowerShell 5.1/WinForms unter Windows erforderlich; Windows-GUI-Runtime-Abnahme ist offen.
