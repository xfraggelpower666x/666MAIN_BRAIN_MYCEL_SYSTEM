---
name: sceeri-windows-projektstarter
description: Erstellt und prüft Windows-Batchdateien für Start, Diagnose, Tests und unterstützte Portable-Builds. Integriert die passenden Starter in ausdrücklich beauftragte Projekt-ZIPs.
---

# Windows-Projektstarter

Nutze bei einem konkreten Projektauftrag den [ToolStarter für Coding](../toolstarter-coding/SKILL.md) zusammen mit [Abnahme und Lieferung](../../references/code-delivery.md). Ermittle aus Quellcode, README, Build-Dateien, vorhandenen Startern und Tests den normalen Einstieg, unterstützte Windows-Umgebung, Laufzeitversionen, Abhängigkeiten, Ausgabeordner und den tatsächlichen Test- oder Build-Befehl.

1. Prüfe vorhandene Starter und deren Aufrufer auf Wiederverwendung. Wenn eine neue oder zu migrierende Windows-Startroutine gebraucht wird, nutze den [ToolStarter-Katalog](../toolstarter-coding/references/catalog.md) und das zum Projekt passende Profil. Dokumentiere einen sichtbaren englischen Doppelklick-Einstieg. Bei ToolStarter ist das STARTEN.bat. Bewahre kompatible Aufrufpfade, Argumente und Exitcodes. Bei Bibliotheken oder statischen Prüfprojekten ist der Einstieg der belegte Prüf- oder Beispielaufruf.
2. Binde vorhandene Prüf-, Test- und Build-Befehle als belegte Aktionen ein. Für fehlende Python-Projektabhängigkeiten verwende die [Python-Karte](../toolstarter-coding/references/cards/python.json) mit derselben Projektumgebung für Probe, Reparatur und Gegenprobe. Der ToolStarter-Launcher selbst braucht bereits CPython ab 3.10. Dokumentiere einen separaten Bootstrap, falls der Build- oder Entwicklungsrechner diesen Interpreter noch benötigt. Erhalte vorhandene nutzbare Umgebungen.
3. `check` und `diagnose` prüfen ohne Installation. Kennzeichne, ob `repair` und `run` Downloads oder Installationen auslösen können. Passe `self_heal_on_run` an den Projektvertrag an. Dokumentiere bei einem Fehlschlag Phase, Log und Rückgabecode. Prüfe [Windows-Lieferabnahme](../../references/windows-lieferabnahme.md) und [Projektsprachen](../sceeri-projektsprachen/SKILL.md#windows-starter). Eigene Texte in Batch- und CMD-Dateien bleiben Englisch. Bei einem bestellten Archiv verpacke die referenzierten Projektdateien mit.

## Zwei Windows-Builds

Binde für diesen Auftrag [STARTEN.bat mit PowerShell-Menü und Dual-Setup](../../references/windows-starten-build.md) ein. Ordne Tool-Proben, Build- und Programmstartaktionen dem Projektprofil zu und übernimm den Compiler aus dem realen Build-Vertrag.

Erzeuge die ausdrücklich bestellten Windows-Artefakte aus derselben geprüften Projektbasis nach den [Windows-Auslieferungsprofilen](../../references/windows-auslieferungsprofile.md). Binde Build und Prüfung für beauftragte Profile in den vorhandenen Projekteinstieg oder in belegte ToolStarter-Aktionen ein. Für die zentrale Entwicklungs-Batch verwende den [direkten EXE-Start der Auslieferung](../../references/windows-auslieferungsprofile.md#ein-entwicklungsstarter). Erhalte vorhandene Portable-Launcher bei einem Bestand ohne beauftragte Umstellung.

Bei Electron und FFmpeg nutze [Electron](../sceeri-electron/SKILL.md) und [FFmpeg](../sceeri-ffmpeg/SKILL.md) zur Wahl der Build-Werkzeuge und zur Prüfung der mitgelieferten Runtime-Dateien.

Im zentralen Projektmenü erhält „Build Windows Setup“ einen eigenen Eintrag und den direkten Aufruf `--setup`. Verbinde ihn mit dem passenden nativen Packager oder mit `toolstarter.py package setup --profile <release-profile>`. Bei vollständiger Windows-Auslieferung prüfe Test, Build, Portable und Setup im angeforderten Umfang. ToolStarter wird als Build-Werkzeug geführt. Die gebaute Anwendung startet selbstständig.

Verwende für den tatsächlichen `cmd.exe`-Einstieg [Windows Batch und CMD](../sceeri-windows-batch-build/SKILL.md). Diese Facette prüft Menü, Argumente, Pfade und Exitcodes. Der Projektstarter bestimmt Aktionen und Toolchain. ToolStarter bleibt die Entwicklungsintegration.
