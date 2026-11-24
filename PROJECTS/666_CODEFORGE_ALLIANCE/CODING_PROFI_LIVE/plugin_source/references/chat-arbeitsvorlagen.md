# Kopierbare Arbeitsvorlagen

| Vorlage | Ausfüllfelder |
| --- | --- |
| Feature | Rolle, Basisrevision, Ziel, gewünschtes Verhalten, betroffene Schnittstellen, Grenzen, Abnahmeszenarien, Lieferung |
| Bugfix | Soll/Ist, Reproduktion, Umgebung, betroffener Einstieg, kleinste Reparatur, Regression, Rückkehrpunkt |
| Refactoring | Ziel, bestehender Vertrag, erlaubte Dateien, zu erhaltende Ergebnisse, Vorher-/Nachher-Prüfung |
| Tests | Verhalten, typische und ungültige Eingaben, Fixtures, Prüfumfang und erwarteter Nachweis |
| UI | Zielgruppe, Hauptaufgabe, Zustände, Navigation, Responsivität, Bedienung per Tastatur und sichtbare Abnahme |
| Projektregeln | Verifizierter Geltungsbereich, Toolchain, Konventionen, Prüfkommandos, Rechte und Ablageort. Bei Bedarf die passende Konvention für AGENTS.md, CLAUDE.md, Cursor oder Copilot im Zielprojekt prüfen. |
| Python-Modul | Zweck, Datei und Einstieg, Datenvertrag, Fehler, Typen, Laufzeitabhängigkeiten, Beispiel und Test |
| Arbeitsstand | Projekt-ID, Datei oder Ref, Basis, ausgewählte Aufgaben, Befunde, angeforderte Aktion, nächste Prüfung |

## Durchgehender Übungsfall

Ein hypothetischer HTML-Formularpfad ruft über TypeScript eine Python-Route auf. Diese publiziert ein Ereignis an einen Java-Consumer. Ziel ist genau eine fachliche Wirkung bei erneuter Zustellung. Bewahre das Antwortschema, den Eventvertrag und gültige Altzustände. Belege zuerst die beteiligten Pfade und Zuständigkeiten. Prüfe Erstzustellung, Wiederholung derselben ID mit gleichem Inhalt und einen Konflikt bei gleicher ID mit anderem Inhalt. Trenne unabhängige Reads für Frontend/API und Event/Consumer. Serialisiere Änderungen am gemeinsamen Vertrag. Speichere bei Unterbrechung Basis, Befunde, offene Tests und Rückkehranker als kopierbaren Handoff. Dieses Szenario ist eine Vorlage.
