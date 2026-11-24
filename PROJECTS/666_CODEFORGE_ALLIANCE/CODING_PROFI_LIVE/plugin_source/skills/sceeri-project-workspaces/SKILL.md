---
name: sceeri-project-workspaces
description: "Prüft bereitgestellte lokale Dateien, Google Drive und GitHub im bestätigten Projektumfang."
---

# Projektquellen

- **Lokal**. Verwende angehängte Dateien, ausdrücklich freigegebene Host-Dateien oder bereitgestellte Diffs. Erfasse Pfade und Quellrevision. Für eine unabhängige Arbeitsfassung gib einen Patch oder eine Dateiliste aus.
- **Drive**. Verwende nur das ausgewählte Objekt oder den Ordner und eine tatsächlich verfügbare Anbindung. Erfasse Herkunft, Version, gelesenen Umfang und eventuellen Export nativer Dokumente. Backups behalten ihre projektseitige Rolle.
- **GitHub**. Verwende den eingegebenen Projektordner als Scope und bestätige Repo, Ref, Pfad und möglichst dieselbe aufgelöste Commit-ID für alle Reads. Unterscheide Suchtreffer, gelesene Inhalte und direkten Readback. Nutze für direkten Zugriff und beauftragte Änderungen den [GitHub-Arbeitsablauf](../../references/github-arbeitsablauf.md). Ohne passenden Zugriff benenne den konkreten Blocker und arbeite mit bereitgestellten Dateien, PR-Diff oder Logauszug weiter.
- **Übergabe**. Halte Quelle, Revision, Umfang, gelesene Inhalte, tatsächliche Prüfsumme und Beleggrenzen fest. Ein Schreibauftrag braucht ein ausdrücklich benanntes Ziel und echte Host-Berechtigung. Änderungen vor Übernahme gegen die Basis prüfen und danach direkt zurücklesen.

## Konsistenz einer Arbeitsgrundlage

Führe pro Datei relativ zum vereinbarten Scope Pfad, Bytezahl, Herkunft, Versionskennung und tatsächlich ermittelte Prüfsumme. Prüfe doppelte oder mehrdeutige Pfade und unvollständige Listen. GitHub-Reads verwenden einen fixierten Commit und ordnen verfügbare Blob-Belege zu. Markiere Submodule und LFS-Zeiger separat. Bei Drive prüfe alle Listenseiten und vergleiche bei verfügbarer Funktion die Ordnerinventare vor und nach den Reads sowie Dateiversionen oder Hashes. Drive-Ordner gelten dabei als nicht atomar. Dokumentiere ausgelassene Verknüpfungen, native Exporte, Caches und nicht lesbare Dateien. Der Host gibt die realen Limits vor.

## Projektgrenzen im Monorepo

Für mehrere Projekte im selben Repository binde je Aufgabe stabile Projekt-ID, eindeutige Aliasauflösung, Wurzel, Ref und exakten erlaubten Pfadbereich. Halte Eigentümer und Verbraucher gemeinsamer Dateien fest. Bestehende Projektgrenzen und vorhandene CI haben Vorrang. Vergleiche normalisierte Pfade, Pfadgrenzen und tatsächlich aufgelöste Zielpfade, bevor ein Write erfolgt. Eine unabhängige zweite Sitzung und eine gezielte Fehlzuordnung dienen als Regression für projektspezifische Rückkehranker, sofern der Host die Sitzungsprüfung unterstützt.
