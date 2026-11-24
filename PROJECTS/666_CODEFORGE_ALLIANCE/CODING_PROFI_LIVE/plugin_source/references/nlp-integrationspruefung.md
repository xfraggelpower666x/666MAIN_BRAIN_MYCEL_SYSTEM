# Abnahme einer Java–Python-NLP-Kette

Bestimme die tatsächlichen Zuständigkeiten. Ein typisches Zielprojekt verwendet Java für Geschäftslogik und Zugriffsschutz, Python für Textverarbeitung und Analyse, HTML für den Bericht. Weise jede Beobachtung dem betroffenen Übergang zu. Übernimm Endpunkte, Frameworks und Versionen aus dem Zielprojekt.

1. **Client → Service.** Prüfe Schema, Zeichencodierung, Zeitlimit und Fehlerzuordnung mit gültiger, fehlender und leerer Eingabe. Unterscheide einen fachlich abgelehnten Inhalt von einem Schemafehler. HTTP 400 und 422 sind die beobachtbaren Sollwerte des gelieferten Beispielvertrags. Für andere Projekte gilt deren Vertrag. Fehlerantworten geben keine internen Details preis.
2. **Analyse.** Trenne deterministische Vertragswerte wie Zeichenlänge und Offsetkonvention von modellabhängiger Entitätserkennung. Prüfe Unicode, kombinierende Zeichen und die Übereinstimmung des Textausschnitts mit den angegebenen Offsets. Lege Modell und Version offen, wenn tatsächlich verfügbar.
3. **Bericht.** Prüfe die HTML-Sprache, fachliche Abschnitte und dass freier Text bei Ausgabe als Inhalt dargestellt wird. Prüfe bei gleichzeitigen Aufträgen auf getrennte Ergebnisse und auf versehentliche gegenseitige Überschreibung. Gib keine Rohtexte oder personenbezogenen Daten in Diagnose-Logs weiter.
4. **Durchgängiger Nachweis.** Berichte getrennt über Python-Test, Java-Clienttest, Ausgabeprüfung und durchgängige Integration. Ein statisch gelesener Test bleibt VORGESCHLAGEN. Der Chat kann Prüffälle und Befunde liefern. Ein tatsächlich laufender Dienst, Sprachmodelle und persistente Berichte benötigen verfügbare Zielprojektwerkzeuge.

Behandle die im Quellarchiv genannte Custom-GPT-Migration und die dort aufgeführten App-Verbindungen als projektspezifische Hinweise. Eine aktuelle Migration oder Anbindung erfordert separat bestätigte Plattformfunktionen.

## Prüffälle aus den Fullstack-Artefakten

Die folgenden Befunde stammen aus der statischen Prüfung der beigefügten Beispiele. Verwende sie als Regressionstest-Entwürfe für ähnliche Zielprojekte. Führe passende Tests nur auf der autorisierten Zielbasis aus und weise deren Ergebnis separat aus.

| Quelle und statischer Befund | Fachliche Gegenprobe |
| --- | --- |
| `service.py`: Bericht wird unter `output/reports/latest_report.html` geschrieben. Der Link zeigt auf `/static/reports/latest_report.html`, dessen Mount auf das paketinterne Verzeichnis `static` verweist. | Erzeuge einen Bericht, rufe genau die zurückgegebene URL auf und prüfe Status, richtigen Inhalt und Zugriffsschutz. Prüfe zwei getrennte Aufträge auf Überschreibung und falsche Zuordnung. |
| `service.py` und `analysis.py`: Das Request-Feld für Sprache steuert das Berichtstemplate, während die Analyse das standardmäßig geladene deutsche Modell nutzt. | Teste zwei unterstützte Sprachen und eine nicht unterstützte Sprache. Gleiche angefordertes Sprachprofil, tatsächlich verwendetes Analysemodell und Berichtssprache mit dem Vertrag ab. |
| `analysis.py`: Rand-Leerzeichen werden vor der Analyse entfernt. Längen und Entitätspositionen beziehen sich auf den bearbeiteten Text. | Prüfe führende Leerzeichen, kombinierende Zeichen und Zeichen außerhalb der Basic Multilingual Plane. Lege Bezugszeichenkette und Einheit fest. Prüfe ausdrücklich, ob Java UTF-16-Indizes und Python Unicode-Codepoint-Indizes umrechnen müssen. |
| `NlpClient.java`: HTTP-Fehler werden innerhalb eines Blocks ausgelöst, dessen allgemeiner Exception-Handler sie als Nichterreichbarkeit umhüllt. | Trenne fachliche HTTP-Antwort, Serverfehler, Timeout, Verbindungsfehler und Thread-Unterbrechung. Prüfe Status und Fehlerursache getrennt. Erhalte den Interrupt-Status. |
| `test_analysis.py` und `test_reporting.py`: Die Analyse lässt sich mit einer kontrollierten NLP-Pipeline prüfen. Der Berichtstest prüft die HTML-Ausgabe getrennt. | Erfasse Satz- und Wortzählung, POS, Lemmata, Entitätstext und Offsets mit einer deterministischen Testpipeline. Prüfe separat, wie der Renderer nutzergenerierten Text behandelt. Prüfe echtes Modellverhalten mit einer ausgewiesenen Modellversion. |

Prüfe außerdem, ob Antwortschema, veröffentlichter Vertrag und Beispielbericht dieselben Felder erwarten. Eine erfolgreiche Kompilierung, ein Test auf Dateiendung und ein erreichbarer Bericht liefern verschiedene Nachweise.
