# G-Helper 0.294 – Build und Abnahme

| Prüfung | Befund |
| --- | --- |
| Originalquellen | ZIP mit `app/GHelper.csproj` enthält Assembly-Version 0.294 und `net10.0-windows`. Die Kopie mit Suffix `(1)` hat denselben SHA-256 wie das ursprüngliche Archiv. |
| G-Helper-Build | .NET SDK 10.0.404 hat für `win-x64` im Release-Modus kompiliert. Der veröffentlichte Host ist eine frameworkabhängige Single-File-EXE mit eigener neuer Prüfsumme. Die Runtime-Konfiguration nennt Microsoft.NETCore.App und Microsoft.WindowsDesktop.App. |
| Setup-Build | NSIS 3.13 hat aus einem Arbeitsordner mit Leerzeichen mit als Fehler behandelten Warnungen eine x64-Setup-EXE erzeugt. Der Compiler meldet sechs Installationsseiten und drei Komponenten. |
| Readback | Das Auslesen mit 7-Zip hat die vier Programmdateien und die drei Hersteller-Installer bytegenau bestätigt. Hersteller-Installer liegen im temporären Setup-Bereich. |
| PowerShell-Prüfung | Beide Skripte wurden geparst. Die Voraussetzungskette bestand simulierte Fälle für Neuinstallation, vorhandene Voraussetzungen, fehlende kompatible ASUS-Hardware und Runtime-Fehlercode 1603. |
| Künftige Versionen | Eine Test-ZIP mit anderem Wurzelordner und Assembly-Version 0.295 wurde erkannt. Eine zum Projekt inkompatible .NET-Reihe wurde abgelehnt. |
| Windows-Abnahme | Die native Ausführung von Batch, grafischem Assistenten und Treibern auf einem ASUS-Gerät bleibt offen. Der Build erfolgte unter Linux. Die Setup-EXE ist unsigniert. |

## Herkunft der Hersteller-Installer

- **PawnIO 2.2.0** – SHA-256 entspricht dem [WinGet-Manifest](https://github.com/microsoft/winget-pkgs/blob/master/manifests/n/namazso/PawnIO/2.2.0/namazso.PawnIO.installer.yaml).
- **ASUS System Control Interface v3.1.73.0** – SHA-256 entspricht dem [ASUS-Support-Download](https://www.asus.com/supportonly/myasus/helpdesk_download/). Version und Hardware-IDs stammen aus `asussci2.inf` im unveränderten Upload.
- **.NET Desktop Runtime 10.0.15 x64** – SHA-512 entspricht dem [Microsoft-Release-Metadatum](https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json). Das Buildpaket speichert zusätzlich SHA-256 zur Eingangsprüfung.

## Neubau aus dem Repository-Projektordner

- G-Helper-Quellarchiv, Desktop Runtime und PawnIO wurden aus den drei hinterlegten Bezugsquellen neu geladen und gegen ihre festgelegten SHA-256-Werte geprüft. Das ursprüngliche G-Helper-Archiv wurde separat erneut akzeptiert. Der ASUS-Installer wurde lokal bereitgestellt und geprüft.
- Der vollständige Neubau mit dem heruntergeladenen G-Helper-Archiv und NSIS 3.13 war erfolgreich. Der Neubau ergab `d1311a2308b735625c8e51ccb2d753f76c60ec41765ba29bb18bd1218ceabd91`. Die separat versionierte Prüfsummendatei dokumentiert den zuvor bereitgestellten Build.

## Korrektur für NSIS 3.13 unter Windows

Das Windows-Protokoll bestätigt Restore und Publish von G-Helper. Die anschließende NSIS-Kompilierung stoppte wegen des fehlenden `Stubs/zlib-amd64-unicode`. Das offizielle Windows-ZIP von NSIS 3.13 enthält die entsprechenden x86-Unicode-Stubs.

`GHelper.nsi` wählt anhand der vorhandenen Stubs und Plugins zwischen amd64 und x86. Der x86-Starter nutzt die 64-Bit-Registry und startet native PowerShell über `Sysnative`. Die x64-Voraussetzung und der x64-Programm-Payload gelten in beiden Varianten. Beide NSIS-Ziele wurden mit als Fehler behandelten Compilerwarnungen geprüft. Zusätzlich hat ein Buildtest mit den Ressourcen aus dem offiziellen NSIS-Windows-ZIP den x86-Pfad bestätigt. Die erneute praktische Prüfung auf Windows steht aus.

## Windows-Pfadkorrektur für den NSIS-Payload

Das zweite Windows-Protokoll erreicht den Kopierabschnitt von NSIS und meldet `payload/GHelper.dll.config -> no files found`. Die Datei war im Publish-Verzeichnis vorhanden. Der Python-Generator hatte `File`-Quellpfade in POSIX-Schreibweise ausgegeben. MakeNSIS zerlegt diese Dateimuster anhand des Pfadtrenners des Buildhosts.

Der Manifestgenerator verwendet jetzt den Pfadtrenner des Buildhosts. Eine Gegenprobe bestätigte die Windows-Ausgabe `payload\GHelper.dll.config` und einen verschachtelten Pfad mit Leerzeichen, sowie die entsprechende Linux-Ausgabe. Die frühere Korrektur für fehlende amd64-Stubs gilt weiterhin. Der erneute Build auf dem Windows-PC steht aus.
