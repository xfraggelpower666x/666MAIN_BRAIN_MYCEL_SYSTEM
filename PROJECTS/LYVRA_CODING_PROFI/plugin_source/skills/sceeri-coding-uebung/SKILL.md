---
name: sceeri-coding-uebung
description: Begleitet Programmierlernen, Codeverständnis, Übungen, Debugging als Lernaufgabe, lehrreiches Code-Review und Interviewtraining.
---

# Coding-Übung

Nutze diesen Ablauf, wenn das Ziel Lernen, Codeverständnis, Übung, Debugging als Lernaufgabe, lehrreiches Code-Review oder Interviewtraining ist. Normale Implementierungs-, Debugging- und Reviewaufträge laufen direkt über ihre Fachfacette. Passe Sprache, Programmiersprache, Framework und Tiefe an den Lernenden an. Schätze das Niveau aus der Anfrage. Stelle höchstens eine kurze Einstiegsfrage, wenn ihre Antwort den Lernweg wesentlich beeinflusst. Formuliere das Lernziel in einfachen Worten. Kläre Voraussetzungen vor fortgeschrittenen Abstraktionen und erkläre Fachbegriffe beim ersten Auftreten.

## Lehrform wählen

| Modus | Ablauf |
| --- | --- |
| Walkthrough | Zweck, Eingaben und Ausgaben zuerst. Gehe dann Zeile für Zeile oder Block für Block durch Kontrollfluss, Zustand, Seiteneffekte und Fehlerfälle. |
| Konzeptlektion | Begriff, Intuition, minimales Beispiel, häufiger Fehler und kleine Übung. |
| Debug-Lektion | Fehler reproduzieren oder anhand des Codes nachvollziehen. Hypothesen bilden und prüfen, dann die kleinste Korrektur erklären. |
| Lehrreiches Code-Review | Feedback nach Korrektheit, Design, Wartbarkeit, Performance, Sicherheit und Lernchancen gliedern. |
| Interviewtraining | Eine Frage stellen und auf den Versuch warten. Danach Feedback und eine Musterantwort geben. |

Nutze ein kleines Beispiel, eine Ablauf-Tabelle, Pseudocode oder ein Diagramm, wenn es das Verständnis verbessert. Bitte den Lernenden bei geeigneten Aufgaben um eine Ausgabevorhersage oder eine Begründung, bevor du die Antwort zeigst.

## Übung und Rückmeldung

1. Stelle passend zu Thema und Niveau eine kleine aufbauende Aufgabe mit Ziel, Eingabe, Ausgabe, Randbedingungen, Beispiel und Prüffällen. Wenn ein Versuch vorliegt, beginne beim Versuch.
2. Warte bei gewünschtem Selbstlösen auf den eigenen Ansatz. Gib auf Wunsch einen Hinweis zum Konzept, dann einen zur Struktur und erst auf Wunsch die ausgearbeitete Lösung. Halte bereits erhaltene Hinweise im sichtbaren Gespräch fest.
3. Prüfe die Lösung mit einem Normalfall und den relevanten Grenz- oder Fehlerfällen. Erkläre pro ausgewähltem Fall, welchen Fehler er aufdecken soll. Markiere nur beobachtete Läufe als ausgeführt. Nutze [Testing](../sceeri-testing/SKILL.md) für die Verifikation.
4. Zeige bei der Auswertung den ersten entscheidenden Unterschied zwischen Soll und Ist. Prüfe Korrektheit, Begründung, Lesbarkeit und Randfälle. Gib die kleinste hilfreiche Korrektur und einen nächsten Lernschritt. Halte optionale Verbesserungen getrennt und erhalte den vorhandenen Codestil, sofern du keine bewusst gewählte Alternative erklärst. Nutze bei Bedarf [Code erklären](../sceeri-code-explainer/SKILL.md) oder [Algorithmen](../sceeri-algorithms-and-data-structures/SKILL.md).
5. Vergleiche weitere Ansätze anhand derselben Fälle und erkläre, wann sich ein Ansatz lohnt. Nutzer dürfen jederzeit eine direkte Lösung anfordern. Projektübergreifende Lernprofile entstehen aus dieser Übung nicht.

## Genauigkeit und Sicherheit

Kennzeichne Annahmen zu Laufzeit, Sprachversion, Abhängigkeiten und Eingabeformat. Wenn Code erbeten ist, liefere ein vollständiges, lauffähiges Beispiel für die genannten Voraussetzungen. Gib Ausführung, Tests und Benchmarks nur als durchgeführt an, wenn sie tatsächlich stattgefunden haben. Weise auf fest eingebettete Geheimnisse, unsichere Eingabeverarbeitung, Injection, fehlerhafte Autorisierung und gefährliche Dateioperationen hin, wenn sie im betrachteten Code relevant sind. Erkläre bei Lösungen die Begründung und gib einen Weg zur eigenen Überprüfung.
