---
name: sceeri-powershell-git
description: Erstellt, prüft und repariert projektgebundene Git- und GitHub-Abläufe mit Windows-Batch als Einstieg und PowerShell als Git-Runtime.
---

# PowerShell · Git und GitHub

Nutze diese Facette bei Git- oder GitHub-Aufträgen mit Windows, CMD, Batch, PowerShell, Bundle oder lokalem Checkout. Für einen reinen GitHub-Connector-Auftrag ohne Windows-Ausgabe gilt der bestehende [GitHub-Arbeitsablauf](../../references/github-arbeitsablauf.md).

1. Ermittle Auftrag, Checkout-Wurzel, Remote und bestätigte URL, Ref, Basis-Commit und gewünschte Ausgaben. Kläre bei Bundle-Aufträgen zusätzlich Archiv, Quell-Ref und Zielbranch. Für Clone, Patch, Commit, Rebase, Tag und Draft-PR prüfe die jeweilige Zielaktion und verwende [Git-Verfahren und Abnahme](references/windows-git.md).
2. Nutze die ausführbaren Vorlagen [STARTEN.bat](assets/STARTEN.bat) und [Git-Workflow.ps1](assets/Git-Workflow.ps1). Binde die PowerShell-Routine bei vorhandenem Projekteinstieg in dessen Menü oder Schalter ein. Bei einem eigenständigen Git-Auftrag liefere die beiden vollständigen Dateien. Passe Zielwerte und erlaubte Aktionen an den Auftrag an. Text außerhalb von Batch-/CMD-Kommentaren in der Batch bleibt Englisch.
3. Status und Remote-Abgleich bleiben lesend. Fetch, Import und Push laufen als getrennte Aktionen. Fixiere beim Auftragsbau Branch und SHA aus tatsächlichen Belegen oder mache sie zu Pflichtparametern. Erzeuge bei Bedarf eine Vorschau. Verwende Git Credential Manager oder die vorhandene SSH-Authentisierung. Secrets gehören weder in Parameterbeispiele noch in Ausgaben.
4. Prüfe die Batch aus einem anderen Arbeitsverzeichnis, den Aufrufpfad mit Leerzeichen, Exitcodes und die PowerShell-Logik im vereinbarten Host. Reproduziere verändernde Verfahren zuerst in einem temporären Repository mit lokalem Bare-Remote. Verwende den echten GitHub-Readback beim ausdrücklich beauftragten Remote-Vorgang. Melde fehlende Hostprüfungen und unklare Schreibzustände mit dem konkreten nächsten Leseschritt.

Kombiniere [PowerShell](../sceeri-powershell-scripting/SKILL.md), [Windows Batch](../sceeri-windows-batch-build/SKILL.md) und die [Git-Karte](../toolstarter-coding/references/cards/git.json). Direkter Einstieg im Plugin: `L.Y.V.R.A. CODING PROFI — POWERSHELL GIT` oder `Erstelle eine Windows-Batch mit PowerShell für [Git-Auftrag]`.

## Tools pruefen, installieren und aktualisieren

Der vorhandene [Batch-Einstieg](assets/STARTEN.bat) leitet `CheckTools`, `InstallTool`, `UpdateTool` und `AnalyzePowerShell` an [Toolchain.ps1](assets/Toolchain.ps1) weiter. Die Tool-Pruefung funktioniert vor Git-Installation und ohne Checkout. Waehle fuer ein Projekt nur benoetigte Werkzeuge. Uebernimm die belegte Node-Version und den vorhandenen Versionsmanager aus dem Projekt. Git, Node.js und Docker Desktop verwenden exakte WinGet-IDs. PSScriptAnalyzer wird ueber PSGallery fuer CurrentUser bereitgestellt. Nach einer Aenderung Paket und tatsaechlichen Aufruf erneut pruefen. WinGet, PowerShell-Host und Docker-Backend als eigene Nachweise behandeln.
