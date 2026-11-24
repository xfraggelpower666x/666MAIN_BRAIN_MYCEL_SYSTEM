---
name: sceeri-pydantic-schemas
description: "Entwirft oder prüft Pydantic-Modelle für API-Eingaben, Ausgaben, Updates, Filter und Batch-Aufträge."
---


# Pydantic-Schemas

Inventarisiere Pydantic-Version, vorhandene Basismodelle, JSON-Verträge, Aliasregeln und ORM-Grenze. Trenne Create, Read, Update und Filter. Unterscheide bei partiellen Updates fehlende Felder von explizitem Null. Verwende eigene Command-, Batch- und Summary-Modelle, wenn sich Vertrag oder Fehlerfälle unterscheiden.

Prüfe Pflichtfelder, Constraints, Default-Werte, unbekannte Eingaben, Serialisierung und Daten, die im Output fehlen müssen. Setze ORM-Serialisierung gezielt an der Read-Grenze ein. Strukturvalidierung liegt im Schema, DB-gestützte oder zustandsabhängige Fachregeln in der zuständigen Fachlogik. Übernimm bestehende Envelope- und Paging-Konventionen. Belege Vertrag anhand positiver und negativer Beispiele und, sofern verfügbar, beobachteter Tests.
