# G-Helper – PC-Kompilierung und Offline-Installer

## G-Helper installieren

1. Nach einem erfolgreichen Build die Datei `GHelper-0.294-Offline-Setup-x64.exe` starten und die Windows-Administratorabfrage bestätigen.
2. Im Assistenten den Zielordner und die gewünschten Verknüpfungen auswählen. Voreinstellung ist `C:\Program Files\G-Helper`. Beim ersten Durchlauf einen neuen oder leeren Ordner wählen. Weitere Builds dieses Setups lassen sich am registrierten Ort installieren, wenn G-Helper geschlossen ist.
3. Bei einer Neustartmeldung Windows neu starten und danach G-Helper öffnen. Die Tastenkürzel stehen im Zielordner in `TASTENKUERZEL.md`.

Das fertige Setup ist offline nutzbar und benötigt natives Windows x64 ab Windows 10 Build 19045. Es führt nötige Voraussetzungen erst nach Start der eigentlichen Installation und aus einem temporären Ordner aus. Die mitgelieferten Installationsprogramme werden nicht im G-Helper-Zielordner abgelegt.

| Voraussetzung | Verhalten |
| --- | --- |
| .NET Desktop Runtime 10.0.15 x64 | Installiert die mitgelieferte Microsoft-Runtime, wenn kein mindestens gleich neuer Patch derselben .NET-10-Reihe vorhanden ist. |
| ASUS System Control Interface v3.1.73.0 | Installiert den beiliegenden ASUS-Treiber für vorhandene Geräte mit `ACPI\ASUS2018` oder `ACPI\ASUS2025`. Eine gleich neue oder neuere aktive Treiberversion genügt. |
| PawnIO 2.2.0 | Installiert PawnIO, wenn kein PawnIO-Treiberdienst registriert ist. |

Die Hersteller-Installer starten mit unterdrücktem automatischem Neustart, soweit der Hersteller einen solchen Schalter vorsieht. Die Setup-Details zeigen übersprungene Komponenten, Rückgabecodes und Fehler. Ein Rückgabecode 3010 meldet einen ausstehenden Neustart. Die Deinstallation von G-Helper lässt gemeinsame Voraussetzungen und die Benutzerkonfiguration bestehen. Falls die frühere selbstenthaltende Setup-Variante installiert wurde, diese vorher über Windows deinstallieren.

## Auf dem PC mit einer Datei starten

Im GitHub-Checkout `PROJECTS/GHelper-Windows-Installer` öffnen. Beim ersten Build den geprüften ASUS-Installer gemäß [Eingaben](eingaben/README.md) in `eingaben\` ablegen. **`GHELPER_BUILD.bat`** doppelklicken und **1** wählen. Das Quellarchiv, PawnIO und die Desktop-Runtime werden bei Bedarf von den in `build-config.json` hinterlegten offiziellen Quellen geladen. Downloads und lokale Eingaben werden mit SHA-256 geprüft. Das Menü bietet außerdem den Ausgabeordner. Der Starter prüft bzw. aktualisiert WinGet und Python 3.14. Python prüft das für das Projekt passende .NET SDK und NSIS, fordert fehlende oder neuere Versionen über WinGet an, lädt die NuGet-Referenzen und baut das Setup. Für diesen Build sind Internetzugang und gegebenenfalls UAC-Bestätigungen nötig. Das ASUS-, PawnIO- und Runtime-Setup wird beim Build nicht ausgeführt.

Die Ergebnisse stehen in `output\`. Zum direkten Bau ohne Menü dient `GHELPER_BUILD.bat installer /nopause`.

## Eine neue G-Helper-Version bauen

1. Das neue Original-Quell-ZIP in `eingaben\` ablegen. Es muss `app/GHelper.csproj` und die zugehörigen Projektdateien enthalten. Archivnamen und Oberordner dürfen sich ändern.
2. Den Dateinamen und die SHA-256-Prüfsumme unter `source` in `build-config.json` anpassen. Den Hash nach Prüfung der Quelle ermitteln. Bei einer lokal bereitgestellten neuen Datei die alten Felder `download_url` und `download_sha256` aus `source` entfernen oder auf die neue offizielle Bezugsquelle und deren Hash umstellen.
3. Wechselt das Projekt auf eine neue .NET-Haupt- oder Nebenversion, das passende **Windows Desktop Runtime x64**-Installationsprogramm in `eingaben\` ablegen. Unter `runtime` Datei, SHA-256 und Version setzen und die Bezugsquelle aktualisieren oder `download_url` entfernen. Der Build leitet die SDK-Hauptversion aus dem Projekt ab und bricht bei einer unpassenden Runtime-Serie ab.
4. `GHELPER_BUILD.bat` starten. Version und Name der neuen Setup-EXE folgen der `AssemblyVersion` im Quellprojekt.

Auch die Installer unter `asus` und `pawnio` sind austauschbar. Bei einem neuen ASUS-Paket die unterstützten Gerätekennungen aus dessen INF übernehmen. Das Paket erwartet die dokumentierten Schalter und Erfolgscodes der mitgelieferten Hersteller-Installer.

```powershell
Get-FileHash .\eingaben\g-helper-NEU.src.zip -Algorithm SHA256
py -3.14 .\build.py --eingaben-pruefen
```

Die G-Helper-Quellen stammen vom [Projekt G-Helper](https://github.com/seerge/g-helper) und enthalten die GPL-3.0-Lizenz. Die gebaute G-Helper-EXE stammt aus diesen Quellen. Die zusätzlich hochgeladene G-Helper-EXE dient nicht als Build-Eingabe.


## Stand für die Weiterarbeit

- Aktueller Quellstand ist G-Helper v0.294, Upstream-Commit `9d1b2a5b79b4ec608c0bc938eef63f3918eecfec`. Die 352 Dateien der beiden Quellarchive sind nach Abzug des ZIP-Wurzelordners bytegleich.
- Am Buildablauf in `GHELPER_BUILD.bat`, `bootstrap.ps1` und `build.py` ändern. Die Auswahlseiten und Deinstallation stehen in `GHelper.nsi`, die Installationslogik für Treiber und Runtime in `install-prerequisites.ps1`.
- Nächste Abnahme auf einem nativen Windows-x64-ASUS-Gerät durchführen. Buildstarter aus einem Pfad mit Leerzeichen starten, Zielordnerwahl prüfen, bei Bedarf neu starten und im Geräte-Manager die ASUS-Treiberversion prüfen. Danach G-Helper und die Wiederinstallation mit bereits vorhandenen Voraussetzungen testen.
- Das Prüfprotokoll und die Prüfsumme der zuvor gebauten Setup-EXE dokumentieren den gelieferten 0.294-Stand. Jeder Neubau erstellt eine eigene Prüfsumme.
