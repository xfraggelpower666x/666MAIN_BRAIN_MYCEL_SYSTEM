---
name: sceeri-provider-integration-acceptance
description: "Prüft Quellzugriff, Provider-Berechtigung, Vertragsgrenzen und Host-Evidenz."
---

# Projektquellen und Anbindungen abnehmen

Nutze [Projektquellen](../sceeri-project-workspaces/SKILL.md). Verifiziere pro angefordertem Zugriff Provider, Projekt-ID, Pfad, Revision und tatsächlich gelesenen Inhalt. Für einen externen Adapter vergleiche Quelle, Owner, Current-Referenz, Commit und Blob, Scope, Rechte, Hostfähigkeit, Rückkehranker und Readback. Bei widersprüchlichen Angaben bleibt die Ausführung blockiert. Ein plausibler Belegverweis ersetzt keinen Abruf.

Für CodeForge, SuperCodeForge und SHEB prüfe Vertrag und echte aufrufbare Schnittstelle getrennt. Belege einen autorisierten Aufruf anhand von Eingabe, Empfänger und beobachtetem Ergebnis. Bei fehlenden Rechten oder Schnittstellen berichte den konkreten Blocker und prüfe unabhängig verfügbare Belege weiter.
