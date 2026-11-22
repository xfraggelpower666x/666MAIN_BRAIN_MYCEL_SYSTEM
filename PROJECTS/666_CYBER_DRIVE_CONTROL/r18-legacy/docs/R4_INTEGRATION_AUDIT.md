# R4 Integrationsaudit

Quelle: https://github.com/adrianiainlam/indicator-keyboard-led (master, öffentlich gelesen, 21.11.2026)

- README: Unity-Indikator der logischen Caps-, Num-, Scroll-Lock-Zustände, freie Reihenfolge `NCS`, versteckbare LEDs, Änderung-basierte Anzeige, optionales Umschalten per xdotool.
- Windows: Unity/GTK und xdotool nicht portiert; stattdessen Win32 `GetKeyState` über vorhandenes Windows-Hardware-Abstraktionskonzept.
- Neue Module: `src/klrw/lock_indicator.py` und `lockindicator_cli.py`.
- GUI: read-only N/C/S-Anzeige mit frei wählbarer Reihenfolge; Polling mit Text-Aktualisierung nur bei Änderung.
- Sicherheitsgrenze: Kein automatisches Tastendrücken; manueller R3-Controller bleibt separat; physische LED nicht garantiert.
- Rechtslage: README nennt MIT-Lizenz für das Python-Skript und Public Domain für SVGs. Keine Quelldateien kopiert.
- Echte Tray-Implementierung, Windows-Host-Abnahme und physische Tastaturprüfung sind OFFEN.
