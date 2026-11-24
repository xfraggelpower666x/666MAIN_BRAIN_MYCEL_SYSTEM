# Entscheidungshierarchie für Coding Profi

Diese Hierarchie gilt für Entscheidungen nach der [Auftragsdeutung](nlp-koordination.md) und dem bestehenden [Routing](coding-profi-zusammenspiel.md#routing-und-vorrang). Der Chat-Einstieg bestimmt Projekt und direkte Absicht. Die Fachfacette untersucht oder ändert den Code. Der [Engineering-Zyklus](engineering-zyklus.md) führt die beauftragten Phasen aus. LiveCircle übernimmt gültige Übergaben. SCEVI zeigt denselben Arbeitsstand. Kleine, eindeutige Aufgaben verwenden dieselben Entscheidungskriterien in Kurzform.

## Reihenfolge der Entscheidungen

| Ebene | Prüfung und Ergebnis |
| --- | --- |
| 1 · Absicht und Scope | Erfasse direkten Auftrag, Ziel, gewünschte Wirkung, ausdrücklich erlaubte Änderungen und Invarianten. Binde Projekt, normale Einstiege und relevante Revision. Trenne gemischte Aufträge je Teilziel und Änderungsumfang. |
| 2 · Code verstehen | Verfolge Eingabe → Einstieg → Aufrufer, Verträge und Zustände → Ausgabe oder Seiteneffekt. Markiere Aussagen als Quellbefund, beobachtete Ausführung oder Hypothese. Prüfe im Umfang des Ziels auch relevante Fehlerpfade. |
| 3 · Befund und Ursache | Vergleiche Soll und Ist. Vergib eine stabile Befund-ID. Trenne Symptom, bestätigten ersten Bruch, plausible Mechanismen und Alternativerklärungen. Bei unklarem Mechanismus wähle eine risikoarme Gegenprobe, die zwischen Erklärungen unterscheidet. Ein eindeutiger Quell- oder Vertragsnachweis kann allein einen Quellbefund tragen. |
| 4 · Entscheidung und Änderung | Wähle die passende Arbeitsart aus der folgenden Tabelle. Binde Änderung an bestätigte Wirkung, betroffene Verträge und zulässigen Scope. Eine neue Beobachtung kann die Arbeitsart fachlich ändern. Der direkte Auftrag bestimmt weiterhin, ob und wo geschrieben wird. |
| 5 · Gegenprobe und Rückmeldung | Prüfe die beabsichtigte Wirkung und die unveränderten Verträge am vorgesehenen Einstieg. Halte Fix, ausgeführte Gegenprobe, Ergebnis und Readback einzeln fest. Bei neuer Evidenz korrigiere die betroffene Entscheidung und abhängige Arbeit im selben Auftrag. Unabhängige Nachweise bleiben nutzbar. |

## Arbeitsarten und Eintrittskriterien

| Arbeitsart | Entscheidungskriterium | Nächster Schritt |
| --- | --- | --- |
| **Verstehen** | Nutzer fragt nach Verhalten, Datenfluss oder Architektur. | Lesend erklären. Fundstellen und offene dynamische Pfade ausweisen. |
| **Audit / Review** | Nutzer will Abweichungen, Risiken oder Qualität bewerten. | Lesend prüfen. Belegte Befunde mit Auswirkung und Gegenprobe liefern. Änderungen als Vorschläge führen. |
| **Reparieren** | Belegter Defekt und erlaubte Änderung. Die Korrektur adressiert einen belegten Mechanismus oder einen direkt nachgewiesenen Vertragsbruch. | Kleinsten fachlich vollständigen Patch am Eigentümer der Funktion anwenden. Ausgangsfall und betroffene Verträge erneut prüfen. Bei unklarer Korrektur zuerst die unterscheidende Probe. |
| **Verbessern** | Bestehendes Verhalten bleibt fachlich erhalten. Das Zielkriterium ist benannt, etwa Verständlichkeit, Antwortzeit oder Wartbarkeit. | Bewährten Einstieg und relevante Invarianten gegen Basis und Kandidat prüfen. Behaupteten Gewinn am passenden Vergleich belegen. |
| **Weiterentwickeln** | Neues Verhalten in einem bestehenden System ist beauftragt. Betroffene Schnittstellen und Verbraucher sind identifiziert. | Erweiterung am passenden Einstieg integrieren. Alte Verbraucher, Versions- und Migrationspfade soweit betroffen prüfen. |
| **Neu erstellen** | Eine neue Komponente oder Anwendung ist beauftragt. Ziel und minimaler nutzbarer Normalpfad sind klar. | Eingaben, Ausgaben, Verantwortung, Fehlerverhalten und Abnahmepfad festlegen. Einen kleinen durchgängigen Ablauf bauen und prüfen. Eine passende bestehende Komponente darf wiederverwendet werden. |

Ein reines Audit bleibt lesend. Ein konkreter Änderungsauftrag führt bei ausreichender Grundlage direkt in die passende Facharbeit. Bei fehlender Ausführungsumgebung bleiben Quellaussagen nutzbar, beobachtete Laufzeitwirkungen offen. Für einen unklaren Schreibausgang prüfe zuerst den tatsächlichen Zielstand. Desktop- und Build-Prüfungen folgen dem konkreten Zielprojekt.

Für Fremdcode gilt zusätzlich der [Fremdcode-Ablauf](engineering-zyklus.md#fremdcode-im-aktiven-architektur--und-codebau). Eine Überarbeitung darf Umfang und Struktur ändern, wenn die wirkungstragenden Beziehungen nachweisbar erhalten oder im beauftragten Sinn weiterentwickelt werden.

## Wie Erkenntnisse die Entscheidung ändern

- **Semantisch:** Eine Nutzerkorrektur aktualisiert die betroffene Absicht und deren Abnahmekriterien. Gleichlautende Begriffe in zwei Komponenten gelten erst mit bestätigter Zuordnung als derselbe Vertrag.
- **Kausal und relational:** Binde Mechanismus und Wirkung über eine benannte Kante an den tatsächlichen Aufrufer, Zustand und Verbraucher. Verfolge relevante transitive Auswirkungen. Ein Importfund allein belegt statische Referenz.
- **Evidenzbasiert:** Halte je wesentlicher Aussage Beobachtung, Quelle oder Test, Revision, Aussagegrenze und Gegenbeleg. Parserbefund, reproduzierter Fehler, Designentscheidung, geschriebene Datei und bestätigte Wirkung sind unterschiedliche Nachweise. Eine fehlgeschlagene Gegenprobe setzt den betroffenen Abschluss zurück.
- **Emergent:** Formuliere eine neue Erklärung oder Verbesserung, wenn Befunde gemeinsam einen prüfbaren Zusammenhang nahelegen. Nenne die beteiligten Befund-IDs, die vorhergesagte Beobachtung, eine plausible Alternative sowie die kleinste Gegenprobe. Ein bestätigter Ausgang korrigiert die betroffene Hypothese und ihre Folgeschritte. Wiederverwendung als Regel setzt belegten Nutzen und benannte Gültigkeitsgrenzen voraus. Neue Anforderungen bleiben ein Vorschlag, bis der Nutzer sie beauftragt.

Bei Übergabe genügen je wesentlicher Entscheidung Arbeitsart, Ziel/Scope, Projektbasis, Befund- und Belegreferenzen, Entscheidung, Gegenprobe und nächster Schritt. Markiere bei Fortsetzung gezielt, welche Annahme, Belege oder Prüfschritte nach einer geänderten Basis oder Nutzerkorrektur erneut gelten müssen.

## Optionale lokale Gegenprobe für die Regeln

Der [Entscheidungsprüfer](../skills/sceeri-code-engineering/scripts/engineering_decision.py) bildet die Reihenfolge für bereits eingestufte Fakten ab. Er prüft keine Quellen und erteilt keine Schreibrechte. Die zuständige Chat-Facette prüft die Fakten und führt die beauftragte Arbeit aus. Die [lokalen Gegenproben](../skills/sceeri-code-engineering/tests/test_engineering_decision.py) sind aus dem Skill-Ordner mit `python -m unittest discover -s tests` ausführbar. Die Fälle in [Chat-Abnahme](chat-abnahme.md) prüfen separat die Wirksamkeit der Regeln im Dialog.
