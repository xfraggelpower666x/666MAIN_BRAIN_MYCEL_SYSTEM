# MENU-8 — Python registered, executable missing / Registry readback

Quelle: Windows-Log 2026-11-21 23:14 CET: Python 3.13.17 und 3.15.2 Komponenten in Windows-Uninstall-Registry, `winget list` Python.Python.3.13, kein funktionsfaehiger Interpreter; MENU-7 meldete READBACK_PENDING.

Befund: Installationsmetadaten sind kein Proof of executable. MENU-7 pruefte nur eingeschraenkte Installationshinweise und dokumentierte existenzlose Kandidaten nicht.

Minimalinvasive Reparatur: zusaetzliche PEP-514 Registry-Views, DisplayIcon/InstallSource, bekannte Launcher-/UV-/pyenv-/Python-Pfade; fehlende EXE-Kandidaten ins JSON aufnehmen. MSI-UninstallString wird ausschliesslich gelesen, niemals ausgefuehrt. Weder Reparatur noch Neuinstallation bei registrierter Installation automatisch ausloesen.

Evidenzgrenze: Windows Registry-/Launcher-Aufloesung ist auf Linux nicht ausfuehrbar; Python-Modultests koennen keinen Windows-Host-Readback ersetzen. Status READBACK_PENDING bis Nutzer-Report.
