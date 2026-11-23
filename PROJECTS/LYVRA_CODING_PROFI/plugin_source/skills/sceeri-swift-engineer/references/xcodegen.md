# XcodeGen im Swift- und Xcode-Build

Wende dieses Profil an, wenn die Projektspezifikation, CI oder ein Projektauftrag XcodeGen belegt. Ermittle die tatsächliche Spec, XcodeGen-Version, Arbeitswurzel, macOS-/Xcode-Version und die für die Abnahme verwendete Destination. Bei koexistierendem Package.swift, Workspace und generiertem Projekt stellt CI oder der belegte Startbefehl fest, welcher Pfad für die betroffene Funktion maßgeblich ist.

1. Verfolge die Spec mit ihren eingebundenen Dateien. Includes werden in Reihenfolge zusammengeführt, anschließend überschreibt die Haupt-Spec. Prüfe bei Include-Objekten den Wert von `relativePaths`, bei Templates die expandierten Targets und Schemes und bei Flags aus Umgebung oder CI den konkreten Aufruf. Halte Secrets und Signing-Werte aus Ausgaben heraus.
2. Prüfe die zusammengeführte Spec lesend, etwa mit `xcodegen dump --spec project.yml --type json`, sofern die eingesetzte Version diese Optionen unterstützt. Prüfe Namen, Plattform, Deployment Target, Sources, Ressourcen, Abhängigkeiten, Build-Konfigurationen und die Test-Targets des gewählten Schemes. Weitergegeben werden nur geeignete Auszüge.
3. Bearbeite für eine beauftragte Änderung die deklarative Quelle und generiere das Projekt mit dem belegten Aufruf, etwa `xcodegen generate --spec project.yml`, in einer isolierten Arbeitskopie. Behandle getrackte generierte Dateien nach der vorhandenen Repository-Konvention. Prüfe Änderungen am Projektgraph und an geteilten Schemes und führe Build-Skripte erst nach Sichtung im beauftragten Scope aus.
4. Rufe auf einem geeigneten macOS-Host `xcodebuild -list` mit dem belegten `-project` oder `-workspace` auf. Führe den Projekt-Build und den vorgesehenen Test mit passendem Scheme und tatsächlich vorhandener Destination aus. Simulator, Gerät, Signierung und Archivierung erhalten jeweils ihren eigenen Nachweis.

| Beobachtung | Aussage |
| --- | --- |
| Include fehlt oder Target unterscheidet sich in der expandierten Spec | Betroffene Konfiguration ist offen oder fehlerhaft. Prüfe zuerst Merge-Reihenfolge und Pfadauflösung. |
| Spec aufgelöst und das Projekt generiert | Spec und Generierung sind im geprüften Umfang belegt. Build und Tests brauchen einen eigenen Lauf. |
| SwiftPM-Test läuft, Xcode oder SDK fehlt | SwiftPM-Ergebnis dokumentieren und betroffene Apple-SDK-Abnahme offen lassen. |
| Haupt-Spec, eingebundene Datei oder Tool-Version ändert sich | Betroffene frühere Generierungs- und Build-Nachweise gegen neue Basis abgleichen. |

Quellbezug: bereitgestelltes XcodeGen-Archiv, README, Docs/ProjectSpec.md, Docs/Usage.md und Sources/XcodeGenCLI/Commands/DumpCommand.swift. Für konkrete Projekte gilt deren dokumentierte XcodeGen-Version.

## Quellarchiv mit Repository-Symlink

Beim beigefügten XcodeGen-Quellstand verweist `Sources/XcodeGenKit/SettingPresets` relativ auf `../../SettingPresets/` innerhalb der Projektwurzel. Prüfe bei beauftragtem Quellimport den aufgelösten Pfad und die erlaubte Quellwurzel vor der Übernahme. Behalte den Symlink nur über einen geeigneten, kontrollierten Git-/Extraktionsweg bei. Vergleiche anschließend auf macOS den generierten Projektgraph mit dem vorgesehenen Ziel. Eine lokal erfolgreiche ZIP-Prüfung belegt diesen Build nicht.
