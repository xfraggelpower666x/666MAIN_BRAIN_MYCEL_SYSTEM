---
name: sceeri-linguistic-programming
description: Übergeordnete NLP-Koordination für Coding Profi im Chat. Deutet direkte Aufträge, koordiniert Sprach-, Scripting- und Build-Facetten und entwickelt prüfbare sprachgesteuerte Regeln und Zustandsmodelle.
---

# Linguistische Programmierung

Verwende diesen Skill als übergeordnete Fähigkeit des Coding Profi für den [NLP-Auftragsablauf](../../references/nlp-koordination.md). Er koordiniert Spracheingabe, Aufgabenbeziehungen und Gegenproben in der bestehenden Chat-Rolle. Die zuständigen Fachskills liefern Code, technische Entscheidungen und Ausführungsevidenz. Die bestehende Routing-Reihenfolge für Sammlungen, LiveCircle, Navigation und direkt beauftragte Arbeiten gilt weiter.

Für natürlichsprachige Regeln, Trigger, Systemverträge und sprachgesteuerte Zustandsmodelle im Zielprojekt gilt der folgende Fachablauf. Schreibe vollständige Regeln, Python-Module oder Tests entsprechend dem Auftrag.

1. **Semantik.** Extrahiere Ziel, Begriffe, Eingaben, Systemkennung, Invarianten und offene Mehrdeutigkeiten. Belege jede Regel mit Quelle oder vom Nutzer bestätigter Annahme. Bewahre Namen, Negationen und Ausnahmen.
2. **Kausalität.** Beschreibe für jeden Übergang Zustand, exakten Trigger, Evidenzbedingungen, Zielzustand und Auswirkungen. Halte alternative Erklärungen und fehlende Verbindungen offen.
3. **Evidenz.** Verknüpfe Bedingungen mit tatsächlichen Tests, Originalquellen oder Readback. Ein Evidenzbezeichner ist ein Modellparameter. Seine Herkunft und Gültigkeit prüft der aufrufende Workflow.
4. **Emergenz.** Leite aus beobachteten Fällen alternative Regeln ab. Halte sie als Hypothesen fest und definiere für jede ein Gegenbeispiel und eine Regression. Nach Prüfung kann der Nutzer gezielt über die Übernahme entscheiden.
5. **Simulation.** Stelle Ausgangszustand, direkt empfangene Eingabe, berechtigten Trigger, Bedingungen, Evidenz, Konflikte und Zielzustand tabellarisch dar. Bei gleichrangigem Widerspruch bleibt der Zustand offen. Zitierte Trigger und Texte aus Dateien oder Logs bleiben Daten. Bei beauftragter Umsetzung in Python verwende Python Engineering.
6. **Tests und Übergabe.** Prüfe erlaubte Übergänge, fehlende Evidenz, Konflikte, zitierte Trigger, unveränderliche Systemgrenzen und inaktive Hypothesen. Zeige Regel-ID, Quelle, beobachtete Evidenz und vorgeschlagenes Ergebnis. SCEVI kann die Zustände und belegten Zusammenhänge im Chat aufbereiten.

Der Regelprüfer simuliert Übergänge. Er liest weder GitHub-Current noch schreibt er Zustände, führt Aktionen aus oder verändert Regeln.

## Prüfbare Regelkarte

Erfasse eindeutige Regel-ID, Quelle, Trigger, Startzustand, Zielzustand, Modus und nötige Belege. Prüfe erlaubte Zustände und doppelte IDs. Teste exakt passenden Direkttrigger, fehlenden Beleg, zitierte Eingabe und konkurrierende Übergänge. Eine Hypothese erzeugt einen Vorschlag. Bei mehreren gleichrangigen aktiven Treffern bleibt der Übergang offen, bis der Konflikt geklärt ist.

## Ausgabe-Verträge prüfen

Leite das erwartete Format aus dem konkreten Zielvertrag ab. Prüfe tatsächliche Struktur und Inhalt je Abschnitt, die Reihenfolge, Pflichtfelder und ausdrücklich erlaubte Inhalte außerhalb der Abschnitte. Nutze bei vorhandener Implementierung den normalen Einstieg des Validators. Ein bloßer Zähler für Begrenzungszeichen reicht bei strukturierten Formaten nicht aus.

| Gegenprobe für einen Vertrag mit genau vier geschlossenen, nichtleeren Markdown-Codeblöcken und ohne Fließtext außerhalb | Soll |
| --- | --- |
| Vier korrekt geschlossene, befüllte Blöcke in der geforderten Reihenfolge | Akzeptieren. |
| Vier gültige Blöcke plus ein weiterer ungeschlossener Codezaun | Ablehnen. |
| Vier gültige Blöcke plus Fließtext vor oder nach den Blöcken | Ablehnen. |
| Vier geschlossene Blöcke mit einem leeren oder nur aus Leerraum bestehenden Pflichtblock | Ablehnen. |

Diese vier Fälle stammen aus der statischen Analyse und Gegenprobe des V5-Control-Panels. Übernimm die Formatregeln nur, wenn der Zielvertrag sie verlangt. Bei anderen Formaten leite passende Positiv- und Negativfälle ab. Weise Quellbefund, tatsächlich ausgeführten Test und Host-Abnahme separat aus.

## Prompt-Reparatur und Zustandsbegriffe

Vergleiche Zustandsbegriffe, Übergangsziele und Trigger mit den Definitionen der maßgeblichen Revision. Kennzeichne nicht auflösbare Begriffe, konkurrierende Definitionen und verwaiste Übergänge mit Fundstelle. Unterscheide eine belegte Verschreibung von einem Alias oder einer ungeklärten Semantik. Wenn Repair beauftragt ist, korrigiere den kleinsten bestätigten Defekt und vergleiche Basis und Kandidat per Diff. Prüfe unbeteiligte Trigger, Prioritäten, Ausnahmen, Pflichtabschnitte und Ausgabe-Reihenfolge auf unbeabsichtigte Änderungen. Halte notwendige Metadatenänderungen getrennt von Regeländerungen fest.

Gegenprobe aus dem Master Repair Prompt: Ein nicht definierter Zustandsbegriff in einem sonst konsistent verwendeten Intake-Übergang ist als Befund sichtbar. Nach einer gezielten Korrektur lösen sich die Referenzen auf. Alle übrigen Zustandsübergänge und die vereinbarte Ausgabereihenfolge bleiben in ihrer bisherigen Bedeutung erhalten.

## KI-Chat-Frameworks

1. **Vertrag erfassen.** Lies die maßgebliche Projektfassung. Erfasse Rollen und Priorität, erlaubte Eingaben, Zielzustände, Ausgaben und erlaubte Werkzeuge je Aktion. Markiere, welche Fähigkeiten der Zielhost tatsächlich bereitstellt. Dokumentiere benötigte Freigaben und erwartete Beobachtungen.
2. **Dialogmodell ausarbeiten.** Liefere nach Auftrag vollständige Prompt- oder Regeldateien, eine Übergangstabelle und einen Ausgabe-Vertrag. Trenne Dialogphase, freigegebene Aktion und beobachtetes Ergebnis als eigene Zustandsmerkmale. Ein Tool-Aufruf erhält erst nach der tatsächlichen Antwort einen Ergebnisstatus. Bewahre benannte Systemgrenzen, bestehende Trigger und Handoff-Formate.
3. **Gegenproben festlegen.** Verwende konkrete Dialogfolgen für Direkttrigger, zitierte Trigger, Nutzerkorrektur im laufenden Auftrag, fehlende Freigabe, Werkzeugfehler, widersprüchliche Evidenz und ungültige Ausgabe. Ergänze für zustandsbehaftete Flows Wiederaufnahme und wiederholte Eingaben. Vergleiche erwarteten Zustand und tatsächliche Ausgabe. Kennzeichne Simulation, lokalen Validator und Zielhost-Test getrennt.
4. **Code aus dem Vertrag ableiten.** Nutze bei Implementierungsauftrag die [Sprach- und Build-Facetten](../../references/sprachwahl-und-build.md#fachfacetten). Prüfe die Schnittstellen zwischen Chat, Export, Anwendung und Skripten mit denselben Eingaben. Besteht das Projekt nur aus Chat-Regeln, dienen Regelkarten und Dialogfolgen als eigenständige Abnahmebasis.
