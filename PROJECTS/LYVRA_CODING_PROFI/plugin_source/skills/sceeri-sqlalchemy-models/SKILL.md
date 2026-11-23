---
name: sceeri-sqlalchemy-models
description: "Entwirft oder prüft SQLAlchemy-Modelle, Metadata, Beziehungen, Sessions und Alembic-Anbindung."
---


# SQLAlchemy-Modelle

1. Ermittle SQLAlchemy-Version, bestehende deklarative Basis, Metadata, Modellimporte und Projektkonventionen. Bei geeignetem 2.x-Stand nutze typisierte Mappings und klare Modulgrenzen.
2. Prüfe Primär- und Fremdschlüssel, Kardinalität, optionale Beziehungen, Nullability, Defaults, Constraints und Löschverhalten. Gleiche Rückbeziehungen ab. Übernimm bestehende Datenbankkonventionen und trenne ORM-Klassen von API-Schemas.
3. Halte Session- und Transaktionsverantwortung an der vorhandenen Fach- oder Servicegrenze. Lade Beziehungen gezielt. Registriere alle relevanten Modelle für [Alembic](../sceeri-alembic-migrations/SKILL.md) und prüfe Imports auf Zyklen.
4. Belege persistiertes Verhalten, Beziehungen, Constraint-Fehler und relevante Abfragen. Bei einer Schemaänderung liefere Migrationsbedarf und Datenverträglichkeit.
