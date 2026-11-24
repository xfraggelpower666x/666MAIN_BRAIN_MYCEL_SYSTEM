---
name: sceeri-python-project-checks
description: Verify Python projects through their configured entry point, test runner, lint and type checks with evidence for each gate.
---

# Python-Projektprüfungen

Verwende diesen Ablauf für projektbezogene Tests, Startprüfungen und Qualitätsprüfungen. Bestehende Einstiegspunkte und Konfiguration haben Vorrang.

1. Lies `pyproject.toml`, vorhandene Testkonfiguration, Lockdateien, CI-Schritte und Projektanleitung. Bestimme die vorgesehene Python-Umgebung und den normalen Einstiegspunkt. Prüfe die verfügbaren Werkzeuge in dieser Umgebung.
2. Plane die kleinste ausreichende Auswahl. Prüfe den betroffenen Aufrufer zuerst, anschließend den relevanten Testbereich. Ergänze die breitere Suite, wenn gemeinsame Schnittstellen, Migrationen oder mehrere Verbraucher betroffen sind.
3. Ermittle die tatsächlich im Projekt dokumentierten Syntax-, Typ-, Lint- und Testkommandos. Nutze sie nur mit einer geeigneten autorisierten Host-Umgebung. Bei fehlender Laufzeit liefere einen Prüfplan und den Status OFFEN. Protokolliere beobachteten Befehl, Umgebung, Rückgabewert und Beleg.
4. Prüfe Seiteneffekte vor Projektstart und Tests. Nutze für Testdaten eine isolierte Umgebung. Fehlende Pakete, Dienste oder ein ungeeigneter Runner sind ein konkreter Blocker für das betroffene Gate. Führe davon unabhängige verfügbare Prüfungen weiter.
5. Pro Gate festhalten: Kommando, Revision, Werkzeugversion, Umgebung, Exitcode, beobachtete Testzahlen und Umfang. Ein Start-Smoke-Test benötigt einen konkreten Nachweis, etwa einen erfolgreich aufgerufenen Einstiegspunkt und das erwartete Ergebnis.

**Abnahme:** Für Start, Tests, Lint und Typprüfung liegt jeweils ein beobachtetes Ergebnis oder ein nachvollziehbarer offener Status vor. Ordne neue Fehler gegenüber bekannten Baseline-Fehlern ein.
