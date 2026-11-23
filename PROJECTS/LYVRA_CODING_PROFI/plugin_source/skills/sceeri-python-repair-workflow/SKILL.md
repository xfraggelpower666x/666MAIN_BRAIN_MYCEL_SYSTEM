---
name: sceeri-python-repair-workflow
description: Reproduce a Python defect, review a minimal patch, and verify the same failure case against the candidate in an isolated working copy.
---

# Python-Reparatur

Verwende diesen Ablauf bei einem konkreten Python-Fehler in bestehendem Code. Für eine reine Untersuchung liefere Befund und Prüfplan. Nutze [Python Engineering](../sceeri-python-engineer/SKILL.md) für Code und [Projektprüfungen](../sceeri-python-project-checks/SKILL.md) für die Abnahme.

1. Erfasse Basisrevision oder Dateihash, normalen Aufrufer, erwartetes und beobachtetes Ergebnis sowie vorhandene Änderungen. Bei einer Arbeitskopie dokumentiere den Quellnachweis.
2. Reproduziere den Fehler mit einem möglichst kleinen fachlichen Regressionstest. Bei verfügbarer autorisierter Laufzeit führe den kleinen Regressionstest auf der Basis aus. Fehlt die Laufzeit, beschreibe den Reproduktionsfall und markiere die Ausführung als OFFEN. Belege die erwartete Fehlermeldung oder Assertion. Ein fehlender Import, ein gesperrter Runner oder ein beliebiger Exitcode belegt den fachlichen Fehler nicht.
3. Verfolge den Kontroll- und Datenfluss bis zur Ursache. Nenne Quellstelle, Beleg und gegebenenfalls eine konkurrierende Erklärung. Halte verbleibende Annahmen offen.
4. Erstelle einen kleinen vollständigen Diff. Vergleiche betroffene Originalzeilen und, sofern messbar, den Basishash vor der Übernahme. Bei abweichender Basis kläre den Konflikt. Markiere Syntax und Laufzeit getrennt.
5. Führe in der Kandidatenkopie denselben Test mit denselben Eingaben und anschließend die betroffenen Regressionen aus. Belege Quelle, Testkommando, erwartete Assertion und beobachtetes Ergebnis. Bei Drift stoppe die Übernahme und verwende `CONFLICT_QUARANTINE`. Bei Regression bleibt der Kandidat gesperrt. Halte Original und Diff für Recovery bereit.

**Abnahme:** Baseline reproduziert den konkreten Fehler, Kandidat besteht denselben Fall und die relevanten Regressionen. Fehlt ein Lauf, kennzeichne die entsprechende Prüfung als `OFFEN`. Liefere einen Diff oder vollständige betroffene Dateien entsprechend dem Auftrag und markiere deren Übernahmestand.
