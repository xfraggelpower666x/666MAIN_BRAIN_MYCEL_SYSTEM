# Visuelle Audit-Abnahme im Coding Profi

Nutze diese Sicht bei einem mehrstufigen Audit, einer visuellen Abnahme oder einem ausdrücklich gewünschten Audit-Monitor. Verwende die IDs und Befunde aus dem [Review Control Center](code-review-control-center.md) und die Projektbasis aus LiveCircle. Wähle die Prüfachsen aus dem Auftrag. Typische Achsen sind Ziel und Scope, Quellstand, normaler Einstieg, kritische Schnittstellen, Navigation, Regression, Artefakt-Readback und Wiederaufnahme. Zeige nur einschlägige Achsen.

## Quoten, Status und Darstellung

- Zähle bestandene Pflichtprüfungen pro vollständig definierter Prüfliste und zeige zuerst den exakten Bruch. Bei unbekanntem oder leerem Nenner bleibt die Quote offen. Einzelne bereits belegte Ergebnisse dürfen sichtbar bleiben.
- Verwende optional einen 20-Segment-Balken. Fülle genau `(20 * bestanden) // gesamt` Segmente. Die ganzzahlige Anzeige ist `(100 * bestanden) // gesamt`. Bei 199/200 erscheinen maximal 99 Prozent und 19 Segmente. Der Bruch trägt die genaue Information.
- Ein belegtes kritisches FAIL oder ein belegtes BLOCKED hält die betroffene Abnahme gesperrt, auch bei hoher Quote. Offene Pflichtprüfungen verhindern PASS. Prüflücken an anderer Revision zählen als offen, bis die Übertragbarkeit verifiziert oder die Prüfung am Kandidaten erneut ausgeführt ist.
- Zeige Befund, Reparatur und erneute Beobachtung unter denselben Befund-IDs. Prüflauf, Freeze, Paket-Readback, Deployment und Host-Abnahme erhalten einzelne Zustände. Die Freeze-Anzeige übernimmt den belegten Freeze-Status aus dem Projekt.
- Nutze den [SCEVI-Vertrag](scevi-visual-contract.md) für Farbe und Textlabels. Eine ausführliche Ansicht zeigt Kandidatenrevision, Abnahmeentscheidung, kritische Befunde, Gegenprobe und Rückkehrpunkt. Die Daemon-Karte erklärt einen Blocker anhand vorhandener Daten. Rechte und Ausführung folgen dem fachlichen Auftrag.

## Optionaler Rechner bei verfügbarem Python-Host

[Audit-Rechner](../skills/sceeri-scevi-visual-intelligence/scripts/audit_summary.py) berechnet die Anzeige aus einer lokalen JSON-Datei per `python audit_summary.py prüflauf.json`. Er erwartet einen bewusst erstellten, revisionsgebundenen Datensatz. Quellen prüfen und Feldwerte vor der Berechnung aus dem eigenen Prüflauf ableiten. Der Rechner prüft Datensatz und Revisionszuordnung und nimmt keine Netzwerk- oder Projektschreiboperation vor. Ohne Ausführung dieselbe Rechenregel anhand belegter Eingaben anwenden und den Lauf des Rechners offen lassen.

```json
{
  "revision": "beispiel-r1",
  "scope_complete": true,
  "checks": [
    {
      "id": "navigation.keyboard",
      "critical": true,
      "result": "PASS",
      "revision": "beispiel-r1",
      "evidence": "Verweis auf den eigenen Testbeleg"
    },
    {
      "id": "host.chat_turn",
      "critical": true,
      "result": "OPEN"
    }
  ]
}
```

Der Beispieldatensatz illustriert das Format. `checks` enthält nur die relevanten Pflichtprüfungen. Jede hat eine stabile ID, `critical` als Boolean und `result` als PASS, FAIL, BLOCKED oder OPEN. PASS, FAIL und BLOCKED brauchen zusätzlich eine nichtleere Evidenzreferenz und die Kandidatenrevision. Bei fehlender oder fremder Evidenz erscheint der Eintrag als OPEN. Sensible Belege über geeignete IDs referenzieren.

| Gegenprobe | Erwartung |
| --- | --- |
| 19 von 20 PASS, kritischer Fehler am Kandidaten | 19 Segmente, 95 Prozent, BLOCKIERT. |
| Alle gelisteten Prüfungen PASS, Vollständigkeit des Umfangs offen | PARTIAL und keine Quote. |
| Erfolgsbeleg an früherer Revision | Betroffene Prüfung OPEN, aktueller PASS bleibt unbestätigt. |
| Alle Pflichtprüfungen am Kandidaten PASS | 20 Segmente und PASS für den Prüflauf. Freeze und Host-Wirkung werden separat geprüft. |
