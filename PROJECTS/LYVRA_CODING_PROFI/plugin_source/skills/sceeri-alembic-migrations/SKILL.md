---
name: sceeri-alembic-migrations
description: "Prüft Alembic-Metadaten, Revisionskette, sichere Rename- und Datenmigrationen sowie Roundtrip-Abnahme."
---


# Alembic-Migrationen

1. Prüfe Alembic-Umgebung, Engine-Konfiguration, Basis-Metadata, Modellimporte und aktuelle Revisions-IDs. Wenn Autogenerate unerwartet leer ist, überprüfe zuerst, welche Modelle tatsächlich registriert sind.
2. Prüfe automatisch erzeugte Änderungen von Hand. Bei beabsichtigter Umbenennung erhalte Daten über Rename oder eine geeignete mehrstufige Migration. Beurteile Typwechsel, Nullability, Constraints, Indizes, Locks und Backfills anhand vorhandener Daten und Dialekt.
3. Behandle bereits angewandte Revisionen als unveränderlich und korrigiere über eine neue Revision. Prüfe Heads und Abhängigkeiten auf Divergenz. Für inkompatible Änderungen plane Expand, Backfill, Umschalten und Contract passend zur laufenden Anwendung.
4. Prüfe in einer entbehrlichen Datenbank Upgrade und, sofern verlustfrei vorgesehen, Downgrade und erneutes Upgrade. Dokumentiere andernfalls einen erprobbaren Restore- oder Roll-forward-Weg. Vergleiche Daten und Schema nach dem Lauf. Produktionsausführung benötigt den konkreten autorisierten Zielauftrag.
