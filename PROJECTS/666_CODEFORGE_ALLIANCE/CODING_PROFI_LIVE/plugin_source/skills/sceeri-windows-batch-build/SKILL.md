---
name: sceeri-windows-batch-build
description: Erstellt und repariert zentrale STARTEN.bat, cmd.exe-Aufrufe und PowerShell-Windows-Buildmenüs für Start, Diagnose, Repair, Test, Portable und Setup.
---

# Windows Batch und CMD für Builds

Nutze diese Facette im konkreten Projektauftrag. Bestätige die maßgebliche Quelle und die Schnittstellen über [Sprachwahl und Build](../../references/sprachwahl-und-build.md).

1. Ermittle vorhandene Schalter, Aufrufer, EXE-Namen, Werkzeugpfade und tatsächliche Architekturen des Projekts. Nutze den [Windows-Projektstarter](../sceeri-windows-projektstarter/SKILL.md) für die belegten Aktionen und die [Auslieferungsprofile](../../references/windows-auslieferungsprofile.md#ein-entwicklungsstarter) für Portable und Setup.
2. Verwende bei diesem Auftrag [STARTEN.bat für Windows-Projekte](../../references/windows-starten-build.md) und die WinForms-Vorlage von ToolStarter. Führe Menü und direkte Schalter auf dieselben Aktionen. Verankere relative Projektpfade an %~dp0, quote Pfade, prüfe Werkzeugverfügbarkeit passend zur Aktion und setze call ein, wenn der Aufrufer nach einem Kind-Batch fortgesetzt werden soll. Prüfe bei choice die Rückgabe einschließlich Abbruch und bei cmd-Blöcken den Zeitpunkt der Variablenexpansion.
3. Sichere den tatsächlichen Exitcode direkt nach dem Kindaufruf. Gib ihn nach popd und eventueller interaktiver Pause zurück. Diagnose bleibt lesend. Für --setup verwende den Projekt-Packager und prüfe, ob die aktuelle Nutzlast zur tatsächlichen Setup-EXE führte.

Prüfe Doppelklick und direkte Schalter mit einem Projektpfad mit Leerzeichen, einem fremden Arbeitsverzeichnis, fehlendem Werkzeug und absichtlich fehlschlagendem Kindprozess unter cmd.exe. Die Entwicklungs-Batch bleibt der zentrale Einstieg. Portable und installiertes Programm starten bei direktem Auslieferungsprofil über die Anwendungs-EXE.

Ruft die Menü-Batch eine PowerShell-Arbeitsroutine auf, prüfe Hostversion, Skriptpfad, Argumente und Rückgabecode zusammen mit der [PowerShell-Facette](../sceeri-powershell-scripting/SKILL.md).

Für eine Git- oder GitHub-Batch verwende [PowerShell Git](../sceeri-powershell-git/SKILL.md). Integriere die Routine in den vorhandenen Einstieg oder liefere bei einem eigenständigen Git-Auftrag den Batch-Einstieg der Facette.
