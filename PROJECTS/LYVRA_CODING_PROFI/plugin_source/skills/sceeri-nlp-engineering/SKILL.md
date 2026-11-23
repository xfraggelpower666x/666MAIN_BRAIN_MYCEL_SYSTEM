---
name: sceeri-nlp-engineering
description: Build, review, and integrate natural language processing in Python, Java, HTML interfaces, and declarative linguistic rules. Clarify missing requirements, then deliver runnable code and practical validation.
---

# NLP Engineering

Nutze diesen Skill bei Aufgaben zur Verarbeitung natürlicher Sprache, etwa Textnormalisierung, Extraktion, Klassifikation oder sprachgesteuerte Regeln. Verwende vorhandene Projektdateien, Tests und Nutzerangaben. Im Coding Profi koordiniert die [linguistische Programmierung](../sceeri-linguistic-programming/SKILL.md) den Auftrag. Diese Fachfacette bearbeitet Zielprojekt-NLP, wenn die Zielanwendung selbst Sprache verarbeitet.

## 1. Ziel und Randbedingungen klären

Stelle vor dem ersten Coding-Schritt bis zu drei kurze Fragen in einer Nachricht, sofern die Antworten den Entwurf verändern. Überspringe bereits beantwortete Punkte. Ist der Auftrag vollständig, bestätige Ziel und entscheidende Vorgaben in einem Satz und beginne.

1. **Aufgabe:** Welche Texte gehen hinein und welches Ergebnis soll herauskommen? Nutze, falls verfügbar, ein anonymisiertes Beispiel mit Soll-Ausgabe.
2. **Integration:** Welche Sprache, Version und vorhandene Schnittstelle soll verwendet werden? Kläre, ob Python oder Java die Verarbeitung trägt, HTML die Oberfläche bildet oder ein linguistischer Regelvertrag gefragt ist.
3. **Grenzen und Erfolg:** Welche Vorgaben gelten für Textsprachen, Datenvolumen, Abhängigkeiten, Laufzeit und Erfolgsmessung? Frage nur nach den Punkten, die für diesen Auftrag relevant sind.

## 2. Implementieren

- Bevorzuge eine verständliche, testbare Lösung. Nutze bestehende Verträge und Werkzeuge. Lege zusätzliche Bibliotheken nur bei konkretem Bedarf fest und dokumentiere Start und Abhängigkeiten.
- Liefere vollständige betroffene Dateien oder den verlangten Patch. Schreibe kurze Inline-Kommentare für Entscheidungen, deren Grund aus dem Code allein schwer ersichtlich ist.
- Prüfe Eingabetyp, leere Eingaben, ungültige Daten und erwartbare Fehler. Gib nachvollziehbare Fehler zurück. Vermeide rohe Texteingaben in Logs, wenn sie vertrauliche Inhalte enthalten können.
- Wähle Unicode-Normalisierung bewusst. Erhalte Originaltext und Zeichenpositionen, wenn Annotationen, Hervorhebung oder Rückverfolgung davon abhängen. Prüfe Mehrsprachigkeit, Leerzeichen und kombinierende Zeichen, soweit sie im Scope liegen.
- Nutze Python- oder Java-Adapter passend zum Zielprojekt. Ein HTML-Frontend behandelt Text als Daten und verbindet sich über die definierte Schnittstelle mit der Verarbeitung. Für explizite Trigger, Bedingungen, Zustände und Konflikte nutze [linguistische Programmierung](../sceeri-linguistic-programming/SKILL.md).
- Halte Zielcode und dessen Laufzeit unabhängig vom Plugin. Nutze [Python Engineering](../sceeri-python-engineer/SKILL.md), [Java Engineering](../sceeri-java-engineer/SKILL.md) oder [Web Engineering](../sceeri-web-engineer/SKILL.md) entsprechend dem Auftrag. Für messbare Optimierung nutze [Python-Performance](../sceeri-python-performance/SKILL.md).

## 3. Testen und integrieren

Liefere einen kurzen Integrationsschritt und passende Prüffälle. Verwende mindestens einen repräsentativen Sollfall und einen relevanten Grenz- oder Fehlerfall. Für Klassifikation oder Extraktion prüfe die Qualität an unabhängigen Beispielen mit einer zum Ziel passenden Metrik. Bei Durchsatz- oder Latenzzielen vergleiche dieselbe repräsentative Eingabe und Umgebung. Nenne die ausgeführten Prüfungen und offene Abnahme knapp.

Bei einem mehrsprachigen Java–Python-Dienst mit HTML-Ausgabe prüfe die Übergänge nach der [NLP-Integrationsprüfung](../../references/nlp-integrationspruefung.md). Ziehe Code- oder Host-Evidenz für den behaupteten Betriebszustand heran.

## Korpusannotation und Sprachgrenzen

Bei Trainings- oder Evaluationskorpora dokumentiere Sprache und Modellversion, Tokenisierungs- und Span-Konvention, Stichprobe, Label-Richtlinien und Umgang mit Uneinigkeit. Prüfe feste Beispiele für Komposita, mehrsprachige oder leere Eingaben und Unicode-Varianten entsprechend dem Zielkorpus. Wenn mehrere Personen annotieren, miss Übereinstimmung vor der Bereinigung auf einer gemeinsamen Stichprobe und protokolliere die Entscheidung bei Abweichungen. Liefere einen kleinen reproduzierbaren Fehlerfall vom Originaltext bis zum Ausgabe-Span.
