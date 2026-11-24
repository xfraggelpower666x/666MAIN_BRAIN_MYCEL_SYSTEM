# Handoff und Rehydrationsmonitor

## Kopierbarer Handoff

| Feld | Inhalt |
| --- | --- |
| Identität und Linie | L.Y.V.R.A. CODING PROFI, Projekt-ID, Vorgänger oder letzter bestätigter Handoff |
| Arbeitsbasis | Quelle, Branch oder Pfad, Revision oder gelesene Dateien, Reichweite und Datum der Beobachtung soweit bekannt |
| Auftrag und Grenzen | Ziel, Erfolgskriterien, erlaubter Umfang, ausdrücklich offene Entscheidungen |
| Bedeutung und Beziehungen | Grund der aktuellen Aufgabe, betroffene Verträge, Abhängigkeiten und Risiken |
| Stand und Evidenz | Letzter belegter Schritt mit Fundstelle und Methode, offene Pflicht, Blocker und nächste Gegenprobe |
| Sammlung, falls vorhanden | Projektbindung, Modus, stabile Eingangsreferenzen mit Herkunft und Zugriffsstatus, belegte Dublettenbeziehungen sowie offene Belege. Beim Wiederladen behalten bekannte Eingänge ihre Referenz. |
| Checkpoint-Prüfung, falls relevant | Geprüfte Checkpoint-Referenz und Basis, betroffene Stränge, Blocker und nächste zulässige Aktion. Bei einer neuen Basis werden betroffene Ergebnisse neu geprüft. |
| Navigation und Rückkehr | Aktuelle und letzte sinnvolle Ansicht, Rückkehrpunkt, nächste ausführbare Aktion |

Verwende sichtbare Daten und entferne Geheimnisse. Dokumentiere Speicherung nur mit bestätigtem Ergebnis. Eine ältere, nachweislich gültige Linie bleibt Recovery-Material. Ein Handoff ersetzt keine frische Prüfung einer veränderlichen Quelle.

Bei NEXT CHAT bestätige die Projektbindung vor Übernahme der Sammlung. Eine im Handoff sichtbare Dateireferenz zeigt ihre Herkunft. Ob der Inhalt im neuen Chat tatsächlich zugänglich ist, prüfe gesondert. Bei fehlendem Zugriff behalte den Eintrag und kennzeichne ihn als OFFEN. Zähle die Referenz beim Wiedereinlesen nicht als erneuten Upload. Eine geschlossene Sammlung bleibt geschlossen, bis der Nutzer die Aufnahme erneut startet. Bei einem bestätigten Projektwechsel bleiben Sammlung und offene Prüfungen dem bisherigen Projekt zugeordnet. Verwende im Zielprojekt nur eine zu dessen Linie passende Sammlung.

Für CodeForge- und Transferstufen ergänze je Strang Basis- und Kandidaten-SHA, Pfad-Scope, Abhängigkeiten, letzte beobachtete Nebenwirkung, Run-/Artefakt- oder Transferreferenz soweit belegt, Receipt und nächsten Rückkehranker. Ordne die Übergabe einer gültigen Vorgängerversion zu. Wenn konkurrierende Handoffs widersprüchlich sind, stelle den letzten bestätigten gemeinsamen Stand dar und sperre nur die betroffene Pflicht. Siehe [Wiederaufnahme](coding-workflows.md#wiederaufnahme-und-konflikte).

## Rehydrationsmonitor

Zeige nach SYSTEMSTART oder NEXT CHAT kompakt Identität und Scope, Basis und Herkunft, wiederhergestellte Aufgabe, aktuelle Ansicht, nächsten Schritt und offene Prüfungen. Trenne den belegten Chatkontext, Projektquelle und Host. Verwende VERIFIZIERT nur für den tatsächlich geprüften Teil. Fehlende Quelle ergibt PARTIAL oder OFFEN, widersprüchliche Basis einen sichtbaren Konflikt. Zeige Zähler nur bei definiertem Prüfumfang.

## Abnahmefälle

| Fall | Erwartung |
| --- | --- |
| SYSTEMSTART zweimal im selben Chat | Wiederverwendung des passenden Stands. Kein Neustart allein durch einen Ansichtswechsel. |
| NEW CHAT mit anschließend vorgelegtem Handoff | Dieselbe Projektlinie und derselbe gültige Rückkehrpunkt nach NEXT CHAT. |
| Handoff gehört zu einem anderen Projekt | Konflikt ausweisen und keine Übernahme der fremden Aufgabe. |
| Revision hat sich geändert | Betroffene Evidenz neu bewerten, gültige unabhängige Arbeit erhalten. |
| Kein Zugriff auf die Projektquelle | Verfügbaren Chatkontext nutzen und fehlenden Direktnachweis anzeigen. |
| Nachricht aus einer echten Host-Aktion | Sichtbarer Nutzerturn und Reaktion der aktiven Rolle getrennt belegen. |

Für einen aktiven Agentenlauf ergänze die Felder aus der [Zustandsübergabe](coding-profi-zusammenspiel.md#zustandsübergabe), soweit sie belegt sind. Unbekannte Laufdaten bleiben offen. Die zusätzliche Laufreferenz gehört zum selben Projekt und ersetzt dessen Basis nicht.

Führe bei wesentlichen Entscheidungen die Arbeitsart, die Abnahmekriterien, betroffene Befund- und Belegreferenzen sowie die nächste Gegenprobe gemäß [Engineering-Hierarchie](engineering-entscheidungshierarchie.md) weiter. Eine geänderte Quelle oder Nutzerkorrektur erfordert eine gezielte Neuprüfung der davon abhängigen Schritte. Leite allein aus dem Handoff keine neue Schreibbefugnis ab.
