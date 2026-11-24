# Git und GitHub unter Windows

Beim Doppelklick liest STARTEN.bat den Status des Checkouts neben der Batch. Um einen anderen Checkout zu nutzen, `-Repository` mit einem vorhandenen lokalen Pfad übergeben. Eine vorhandene Projekt-Batch kann dieselbe PS1 mit festem Skriptpfad und denselben Argumenten aufrufen. Die Vorlage benötigt Git und Windows PowerShell 5.1 oder PowerShell 7. Bei Bedarf richtet der bestehende ToolStarter die projektbezogene Git-Prüfung ein.

| Aktion | Erwartete Eingaben | Ergebnis |
| --- | --- | --- |
| Status | Checkout | Status, Branch und lokaler HEAD |
| VerifyRemote | Remote, exakte bestätigte GitHub-URL und Branch, optional Commit | Exakter Branch-Head oder fehlender Branch |
| Fetch | Wie VerifyRemote | Branch-Objekte und FETCH_HEAD. Keine Änderung am Arbeitsbaum. |
| VerifyBundle | Bundle-Pfad, enthaltene Branch-Ref als Kurzname und vollständiger Commit | Git-Prüfung von Ref, Commit und Voraussetzungen |
| ImportBundle | Wie VerifyBundle, zusätzlich neuer lokaler Zielbranch | Vorschau. Mit `-Apply` legt die Routine den Zielbranch erstmals atomar an und liest ihn zurück. |
| Push | Verifizierte GitHub-URL, Branch, vollständiger lokaler Commit und erwarteter Remote-Commit oder `missing` | Git-Push-Vorschau. Mit `-Apply` erfolgt ein regulärer Non-Force-Push mit anschließendem Remote-Abgleich. |

Bei einem beauftragten Push produziere Startbefehl und Belege mit genau einem Ziel. Der Remote-Abgleich unmittelbar vor einem regulären Push ersetzt keine atomare Remote-Vorbedingung. Git lehnt nicht vorwärtsgerichtete Änderungen ab. Wenn der Auftrag eine exakte atomare Remote-Precondition erfordert, benutze die autorisierte Ref-API oder einen neuen eindeutig benannten Arbeitsbranch. Falls ein Push einen Fehler oder eine unklare Rückgabe liefert, prüfe zuerst `VerifyRemote` gegen den erwarteten Ergebnis-Commit.

## Weitere Git-Aufträge als projektgebundene Variante

- Clone: bestätigte URL und Zielpfad, vorhandenes Verzeichnis früh prüfen, Branch und erwarteten Commit nach Lesen belegen.
- Diff, Patch und Commit: erwartete Basis, exakte Dateien einschließlich Umbenennungen, Arbeitsbaum und Index vergleichen. `git apply --check` und relevanten Test vor beauftragtem Apply ausführen. Nur freigegebene Pfade stagen und den Ergebnis-Commit direkt lesen.
- Merge, Rebase und Tags: Autorität, Ausgangsref und Ziel einzeln prüfen. Konflikte sichtbar anhalten und zuständige Aktion dokumentieren. Branch- oder Tag-Löschung und Force-Updates brauchen einen eigenen konkreten Auftrag.
- Bundle erzeugen: bestätigten Ref und vollständigen Commit festhalten. Archiv nach Erstellung mit Hash, Ref-Liste und Git-Verifikation nachlesen. Bei Import zuerst die benötigten Voraussetzungen prüfen.
- Pull Request: autorisierten GitHub-Connector oder bereits eingerichtetes `gh` verwenden. Einen angeforderten Draft mit den exakten Head- und Base-Refs erstellen und direkt zurücklesen. Push und Merge bleiben eigene Aktionen.

## Abnahme

Teste Leerzeichen im Repo- und Skriptpfad, fremdes Arbeitsverzeichnis, fehlendes Git, falsche URL, falschen SHA, bestehenden Bundle-Zielbranch, Ref-Drift, abgewiesenen Push und korrekten Batch-Exitcode. Windows-Abnahme getrennt für CMD und die tatsächlich unterstützte PowerShell. Verwende SCEVI für Status, letzten gesicherten Commit, nächsten zulässigen Schritt und beobachteten Readback.

## Werkzeugpflege und Analyse

Lege `Toolchain.ps1` neben `Git-Workflow.ps1`. Der vorhandene Batch-Einstieg reicht die Parameter durch. Fuehre Installations- und Aenderungsaktionen fuer das jeweilige Ziel aus einer passenden Windows-Sitzung aus. Das Tool-Setup funktioniert ohne Checkout.

```bat
STARTEN.bat -Action CheckTools
STARTEN.bat -Action InstallTool -Tool Git
STARTEN.bat -Action InstallTool -Tool Git -Apply
STARTEN.bat -Action UpdateTool -Tool Node -NodeChannel LTS -Apply
STARTEN.bat -Action InstallTool -Tool Docker -Apply
STARTEN.bat -Action InstallTool -Tool PSScriptAnalyzer -Apply
STARTEN.bat -Action UpdateTool -Tool PSScriptAnalyzer -Apply
STARTEN.bat -Action AnalyzePowerShell -ScriptPath "C:\Mein Projekt\Git-Workflow.ps1"
```

CheckTools liest vorhandene Versionsausgaben. npm wird separat angezeigt. Docker meldet CLI und Erreichbarkeit des lokalen Windows-Engines getrennt. Der CLI-Nachweis alleine ist keine Engine-Abnahme. Exitcode 3 bedeutet, dass mindestens ein angefordertes Werkzeug im aktiven Host fehlt oder seine Versionsprobe scheitert. InstallTool und UpdateTool nehmen jeweils ein Werkzeug. Ohne Apply zeigt die Routine den vorgesehenen Schritt. Ein vorhandener Node-Versionsmanager bleibt die fuer diese Installation zustaendige Quelle. Nutze Current nur fuer Projekte mit diesem Kanal. Fuer einen belegten Versionspin steht ToolVersion zur Verfuegung.

AnalyzePowerShell nutzt zuerst den nativen Parser und anschliessend die PSScriptAnalyzer-Standardregeln. Fehler liefern Exitcode 1. Warnungen und Hinweise bleiben sichtbar. Die Option fuehrt die zu analysierende Datei nicht aus und aendert sie nicht. PSScriptAnalyzer prueft Text in einem einzelnen Skript. Bei verlinkten Modul-/Manifestdateien sind zusaetzlich deren eigene Tests noetig.

Pruefe nach Setup Paket und aktiven CLI-Pfad im tatsaechlichen Windows-Host. Ein offener PATH-Readback wird gemeldet. Bei Docker sind ein gestartetes Backend und eine erneut ausgefuehrte lokale Engine-Probe erforderlich.
