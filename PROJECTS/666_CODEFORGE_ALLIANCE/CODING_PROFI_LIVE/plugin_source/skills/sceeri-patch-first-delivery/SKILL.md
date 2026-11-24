---
name: sceeri-patch-first-delivery
description: Prepare a scoped patch against a pinned baseline, preserve unrelated project content, and verify the exact delivered change before adoption.
---

# Gezielte Patch-Übergabe

1. Fixiere die Ausgangsrevision oder die Datei-Hashes. Bestimme betroffene Aufrufer, Schnittstellen und erlaubte Pfade.
2. Entwickle den kleinsten vollständigen Kandidaten in einer separaten Arbeitskopie. Erfasse je geänderter Datei alten und neuen Hash sowie den Zweck. Erhalte unbeteiligte Dateien und bestehende Projektkonventionen.
3. Prüfe den Diff, den betroffenen Einstieg und die Regression. Bei neuer Basis kläre Abweichungen vor Übernahme. Nutze [Python-Reparatur](../sceeri-python-repair-workflow/SKILL.md) für konkrete Fehler.
4. Gib den verlangten Patch oder vollständige betroffene Dateien zusammen mit Basisnachweis und Rückkehrpunkt ab. Bei autorisierter Übernahme lies die tatsächlichen Zielbytes zurück. Eine Release-Umschaltung gehört an das Ende des zuständigen Update-Verfahrens.

Bei ähnlichen Fundstellen oder abweichender Basis nutze die [Kontext- und Patchprüfung](../../references/sweep-arbeitsablaeufe.md).

Nutze für den fertig geprüften Zielprojektstand zusätzlich den [Projektabschluss mit optionalem ZIP-Export](../../references/code-delivery.md#verbindlicher-projektabschluss). Ein ausdrücklich nur als Patch beauftragter Umfang bleibt begrenzt.
