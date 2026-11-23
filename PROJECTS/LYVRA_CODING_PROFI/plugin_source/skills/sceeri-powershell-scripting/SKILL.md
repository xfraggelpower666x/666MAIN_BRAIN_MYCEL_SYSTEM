---
name: sceeri-powershell-scripting
description: Schreibt, prüft und repariert PowerShell-Automation und Build-Skripte für Windows PowerShell und pwsh.
---

# PowerShell

Nutze diese Facette im konkreten Projektauftrag. Bestätige die maßgebliche Quelle und die Schnittstellen über [Sprachwahl und Build](../../references/sprachwahl-und-build.md).

1. Identifiziere powershell.exe oder pwsh, Hostversion, Module, Aufrufer und Arbeitsverzeichnis. Nutze belegte Voraussetzungen und bestehende Richtlinien.
2. Verfolge Argumentarrays, LiteralPath, PSScriptRoot, native Rückgabecodes und PowerShell-Fehler. Gib den Fehlercode am Übergang zu Batch oder CI im vorgesehenen Vertrag zurück.
3. Nutze die Parserprüfung und vorhandene Pester-Tests. Prüfe Host, Encoding, Pfade mit Sonderzeichen und den konkreten Aufruf mit fehlschlagendem nativen Prozess.

Verwende die Gegenprobe passend zum direkten Auftrag und gleiche betroffene Build- und Skriptpfade im selben Kandidaten ab.

## Windows-Automation und ToolStarter

Wähle Windows PowerShell 5.1 (`powershell.exe`) oder PowerShell 7 (`pwsh.exe`) anhand des bestehenden Aufrufers, der Module und des Zielhosts. Wenn beide unterstützt werden sollen, prüfe die verwendete Syntax, Module und das Encoding in beiden Hosts. Richte Dateipfade bei Aufrufen aus anderen Arbeitsverzeichnissen am vorgesehenen Skript- oder Projektpfad aus.

Ist eine zentrale `STARTEN.bat` vorhanden oder beauftragt, behält sie als Einstieg Menü, Weitergabe der Profilparameter und Rückgabe des Exitcodes. Diagnose, Build und Setup können die PowerShell-Arbeitslogik mit einem festen Argumentvertrag aufrufen. Nutze für die Abnahme das [Windows-Laufzeitprofil](references/windows-laufzeitprofil.md) und bei einem Paketauftrag die [ToolStarter-Integration](../toolstarter-coding/references/integration.md).

## Git und GitHub

Bei lokalen Git-Aufträgen, Bundle-Transfer und GitHub-Veröffentlichung über PowerShell verwende [PowerShell Git](../sceeri-powershell-git/SKILL.md). Die Facette enthält ein geprüftes Aufrufmuster mit Argumentarrays, Ref- und SHA-Abgleich sowie Batch-Exitcode.

Fuer PSScriptAnalyzer nutze die [Windows-Werkzeugpflege](../sceeri-powershell-git/references/windows-git.md#werkzeugpflege-und-analyse). Fuehre Parser und PSScriptAnalyzer im vorgesehenen Host aus. Gib Analysefehler, Warnungen und noch ausstehende Laufzeitpruefungen getrennt an.
