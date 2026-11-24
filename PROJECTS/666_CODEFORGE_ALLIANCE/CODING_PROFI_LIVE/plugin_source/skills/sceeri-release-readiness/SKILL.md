---
name: sceeri-release-readiness
description: "Prüft Release- und Deployment-Bereitschaft, CI-Nachweise, Migrationen, Smoke-Tests und Rollback-Kriterien."
---

# Release-Abnahme

1. Erfasse Dienst, Zielumgebung, Release-ID, Commit und Artefakthash. Ordne Diff, Review und CI-Ergebnis genau diesem Stand zu. Fehlende Belege bleiben OFFEN.
2. Prüfe vor der Auslieferung die Abwärtskompatibilität von APIs und Datenbankmigrationen, Abhängigkeiten, Konfiguration und Feature Flags. Lege fest, wer freigibt und wer bei einer Störung übernimmt.
3. Beschreibe Staging-Smoke-Tests, kritische Nutzerpfade und gegebenenfalls Canary-Stufen. Definiere je Messgröße Baseline, Beobachtungsfenster, Schwelle und Zuständigkeit. Metriken wie Fehlerrate und p95-Latenz brauchen einen passenden Projektbezug.
4. Dokumentiere Abbruchkriterien, Rollback-Ziel und Datenverträglichkeit beim Zurückrollen. Bei irreversiblen Migrationen plane Wiederherstellung oder Roll-forward mit Beleg.
5. Liefere eine Checkliste für vor, während und nach der Auslieferung mit Beleg, Status und nächster Aktion. Trenne Staging-Ergebnisse von Produktionsmessungen. Deployment, Benachrichtigungen und Ticketänderungen benötigen jeweils den passenden autorisierten Auftrag.

Für Artefakt-Readback und getrennte Abnahmen verwende [UCA-R02-Integration](../sceeri-uca-r02-integration/SKILL.md).
