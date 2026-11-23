# Agentenlauf und Produktionsreife prüfen

Nutze die beiden Add-ons als Quellen für Architektur- und Abnahmefragen. Coding Profi analysiert Entwürfe, vorgelegten Code, Konfigurationen und tatsächliche Laufbelege. Projektbezogene Ausführung und Wiederaufnahme folgen den verfügbaren Werkzeugen und dem bestätigten [LiveCircle](coding-profi-livecircle.md).

## Lauf und Abhängigkeiten

1. Erfasse Ziel, Revision, Projektgrenze und belegten Arbeitsstand. Unterscheide Validierung, Planung, Warten auf Eingabe oder erforderliche Freigabe, Ausführung, Verifikation und Endzustand. Ohne beobachteten Übergang bleibt die nächste Phase geplant.
2. Weise Aufgaben Verantwortlichkeiten, Eingaben, Ausgaben und echte Vorgänger zu. Prüfe eindeutige IDs, auflösbare Abhängigkeiten und Zyklen. Gib eine Aufgabe erst frei, wenn ihre notwendigen Vorgänger belegt abgeschlossen sind. Unabhängige Reviews und fachliche Prüfschritte können getrennt bewertet werden. Eine Rollenbezeichnung belegt keinen gestarteten Agenten.
3. Prüfe vor einem Zielprojekt-Werkzeugaufruf registrierte Fähigkeit, Eingabeschema, Ziel, zulässigen Scope, Zeitlimit und tatsächliche Auswirkungen. Verwende die bestehende Autorisierung. Prüfe bei einem Freigabeschritt, dass er an Aktion, Ziel, Parameter und Lauf gebunden ist und dass die Ausführung diese Entscheidung tatsächlich prüft.
4. Verifiziere das Ergebnis anhand beobachteter Ausgaben oder Rücklesen. Unterscheide erfolgreiche Tool-Antwort, erreichten Projektzustand und bestandene Abnahme. Sichere Checkpoints nach der Projektregel und verifiziere den tatsächlich wiederherstellbaren Stand, einschließlich offener Aufgaben und letzter bestätigter Nebenwirkung.

## Architekturabnahme für autorisierte Zielprojekte

| Prüfbereich | Erwarteter Nachweis |
| --- | --- |
| Identität und Datenzugriff | Gültige Identität aus der autoritativen Quelle, geprüfte Rolle und serverseitige Bindung von Lauf, Checkpoint und Abruf an das Projekt oder den Mandanten. Prüfe das Ablehnen fremder Ressourcen mit isolierten Testdaten. |
| Retrieval | Berechtigungen beim Indizieren und beim Abruf, Version und Herkunft von Index und Dokument, datensparsame Verarbeitung und kontrollierte Aktualisierung. Kennzeichne einfachen Textabgleich getrennt von beobachteter Vektorsuche. |
| Persistenz und Recovery | Geprüfte Migration, Backup und Restore, nachvollziehbare Zuordnung zum Lauf und Fortsetzung ohne doppelte Nebenwirkung. Speicher im Prozess, Cache und dauerhafte Quelle getrennt beurteilen. |
| Laufzeitgrenzen | Belege zu tatsächlich erzwungenen Dateisystem-, Netzwerk-, Prozess- und Ressourcenlimits. Eingabeprüfung und Befehlsliste sind eigene Kontrollen. |
| Repository und CI | Beobachteter Provider, Repository, Revision und Run. Prüfe tatsächliche Scopes und ob Status, Logs sowie Tests zur gleichen Revision gehören. |
| Telemetrie und Audit | Verknüpfe beobachtete Lauf-, Trace- und Schritt-IDs. Erfasse Status, Dauer, Tool, Ergebnis, Policy-Entscheidung und Kosten nur bei verfügbaren Messwerten. Redigiere sensible Inhalte. Prüfe Export, Aufbewahrung und Nachvollziehbarkeit getrennt. |
| Evaluation | Versioniere Fall, erwartetes Verhalten, Datensatz und Prüfkriterium. Berichte Test-, Tool- und Run-Ergebnisse mit eigenem Nenner. Bei NLP-Evals gleiche Annotation und Labeldefinition ab, bevor Precision, Recall oder F1 verglichen werden. Setze Grenzwerte anhand des Zielprojekts. |

## Statisch beobachtete Grenzen der Vorlagen

- Das Core-Beispiel hält die Freigabe in einem In-Memory-Dienst. Die gelesene Tool-Route meldet bei Bedarf eine erforderliche Freigabe. Eine durchgängige geprüfte Freigabe bis zur Wiederaufnahme ist dort nicht belegt.
- Das Production-Beispiel verwendet einen als Platzhalter bezeichneten Identitätsresolver. Der gelesene Checkpoint-Handler liest nach Run-ID. Die Mandantenprüfung muss am tatsächlichen Leseweg belegt werden.
- Die Production-Event-Route sendet zeitgesteuerte Beispielereignisse bis COMPLETED. Das belegt eine Ausgabesequenz und keinen abgeschlossenen Lauf. Ein Dashboard muss Status und Fortschritt aus realen Schrittbelegen ableiten.
- Im Production-Beispiel prüft der Orchestrierungstest Rollen und einen Konfliktfall. Verifizierte Abhängigkeitsauflösung und vollständige Wiederaufnahme benötigen eigene Beobachtungen.
- Telemetrie-Export und dauerhafter Audit-Speicher erfordern eigene Abnahme. Die Vorlage zeigt eine In-Memory-Sammlung für Audit-Einträge. Ein Komponentenname oder eine Compose-Datei genügt als Nachweis nicht.

## Quellenabgleich

`agent-runtime-core-addon.zip` (27 Einträge) und `production-agent-platform-addon.zip` (41 Einträge) lieferten die neuen Prüfpunkte für Laufzustände, Policy, Abhängigkeiten, Persistenz, Retrieval, CI, Telemetrie und Evaluation. Die geprüften Vorlagen wurden statisch gelesen. `fullstack-code-nlp-agent.zip` (38) und `coding-intelligence-visual-addon.zip` (17) sind bytegleich mit den Unterarchiven aus dem früheren Paket. `artifacts(2).zip` hat dieselben 57 Pfade und dieselben Nutzdaten wie `artifacts(1).zip`. Deren Prüffälle stehen im [bisherigen Quellenabgleich](integration-v035.md).

## Operative Gegenproben

- **Werkzeugvertrag:** Prüfe anhand eines vorgelegten Schemas Name, erforderliche Felder, Typen, unbekannte Felder und erwartete Ausgabe. Trenne dokumentierte Regeln, tatsächlich durchgesetzte Regeln und UI-Anzeige. Im Core-Beispiel prüft das Register Feldnamen und Pflichtfelder. Typ- und Ausgabeschemata brauchen eigene Nachweise. Führe bei bloßem Review keine Beispielbefehle aus.
- **Lauf und Freigabe:** Gleiche Run-ID, Projekt, Identität, Aktion und konkrete Parameter vor und nach einer Freigabe ab. Prüfe eine bereits verwendete oder nicht zum Lauf passende Freigabe anhand isolierter Sollfälle. Für den Aufgabenplan prüfe, ob die Vorgängerbezeichnungen tatsächlich zu den vergebenen IDs passen. Im Production-Beispiel verwendet der Plan feste Vorgängerbezeichnungen, während das Task-Modell IDs erzeugt.
- **Wiederaufnahme:** Prüfe Zustand, Revisionsbezug, fehlende Aufgaben, letzte belegte Nebenwirkung und deren Wiederholbarkeit. Prüfe bei einem bereitgestellten Zielprojekt die Hin- und Rückumwandlung eines Checkpoints. Das Production-Beispiel speichert eine Textdarstellung und liest eine Zeichenkette zurück. Eine typisierte Rehydration braucht zusätzlichen Nachweis.
- **Gedächtnis:** Trenne Arbeitsstand, beobachtete Ereignisse, belegte Fachfakten und bestätigte Verfahrensregeln. Verwirf veraltete oder fremde Evidenz. Eine als hoch bezeichnete Konfidenz ersetzt keinen überprüfbaren Fall. Im Chat nutze sichtbare Belege und bestätigte Handoffs.
- **Evaluation:** Bei vorliegenden Soll-/Ist-Daten prüfe konkrete Werte, Grenzfälle und Fehlerpfade. Fehlende Angaben zu Regression oder Sicherheit bleiben OFFEN. Für NLP-Entitäten verwende die vereinbarte Identität, etwa Dokument, Label, Start und Ende. Weise TP, FP und FN aus. Precision ist TP/(TP+FP), Recall ist TP/(TP+FN), F1 ist das harmonische Mittel. Lege den Fall leerer Mengen nach dem Zielvertrag offen.
- **Telemetrie:** Gleiche Run-, Trace- und Schritt-Belege ab. Vergleiche Metriken über denselben Scope. Ein Test für einen In-Memory-Zähler belegt die Zählung, ein beobachteter Export belegt separat die Telemetrieanbindung.
- **Provider und Isolation:** Werte tatsächliche Repo-/CI-Readbacks aus oder analysiere vorgelegte Logs. Ein geplanter PR/MR ist ein Entwurf, bis der autorisierte Provider ihn bestätigt. Lese- und Schreibrechte, Identitätsprüfung, Ressourcenisolation und Datenspeicherung bleiben getrennte Nachweise.

### Abnahmeszenarien für den Chat

| Eingabe | Erwartung |
| --- | --- |
| A belegt abgeschlossen, B blockiert, C hängt von B ab | C bleibt blockiert. A bleibt abgeschlossen. Ein unabhängiger lesender Prüfschritt kann weitergehen. |
| Statusliste enthält nur geplante Zeitereignisse und COMPLETED | Abschluss im Zielprojekt bleibt OFFEN. Zeitereignisse werden als vorgelegte Ausgabe ausgewiesen. |
| Gold: zwei Entitäten. Ist: drei, davon eine identisch | TP 1, FP 2, FN 1. Precision 1/3, Recall 1/2, F1 2/5. |
| Handoff enthält abweichendes Projekt oder Revision | Widerspruch markieren. Den bestätigten Stand getrennt halten und fehlenden Nachweis benennen. |

## Lokale Belegprüfung

Aufruf aus der Pluginquelle mit Python ab 3.10:

```text
python skills/sceeri-agentenlauf-chat/scripts/check_run_evidence.py contract.json receipt.json ./artefakte
```

- Der vorab definierte Sollvertrag und der aus dem Lauf stammende Istbeleg haben jeweils `schema: 1`, `project`, `revision`, `run_id` und `steps`. Der Laufbeleg übernimmt seine Identität aus der tatsächlichen Ausführungsumgebung. Erstelle die Erwartungsdatei unabhängig vom beobachteten Ergebnis.
- Soll-Schritte enthalten `id`, `requires` (Liste der Vorgänger-IDs), `exit_code` (Ganzzahl) und `artifacts` (relative Dateipfade auf erwartete SHA-256 in Kleinbuchstaben). Bei einem fachlichen Seiteneffekt prüfe den tatsächlichen Beleg. Für Schritte mit leerer Artefaktliste wird nur die deklarierte Exitcode-Erwartung geprüft.
- Ist-Schritte enthalten `id`, `state` (`completed`, `interrupted`, `timeout` oder `blocked`) und bei `completed` den `exit_code`. Verwende `completed` auch bei einem beobachteten regulären Fehlerexit. Nutze einen eigenen Artefaktordner pro Lauf und unterscheidbare Belegdateien je Schritt. Benutze einen neuen Beleg für einen neuen Lauf.
- Der Prüfer führt keine Befehle aus. Er validiert Projekt, Revision, Lauf, gerichtete Vorgänger und Dateihashes. Ein Abbruch oder fehlender Beleg lässt den Schritt offen. Abhängige Schritte bleiben ohne bestandene Vorgänger blockiert. Exitcode 0 meldet vollständigen Abgleich, 1 meldet Abweichung oder offene Schritte, 2 eine ungültige Eingabe. Ein lokal ausgelesener Hash weist den Dateiinhalt nach. Herkunft, Laufzeit und Produktionsstatus folgen den unabhängig verfügbaren Quellen.

### Herleitung aus den bereitgestellten Archiven

| Archiv und Quellstelle | Wirkung im Coding Profi |
| --- | --- |
| OpenAI Python SDK, `src/openai/_base_client.py` 898–950 und 1149–1151 | Bedingte Wiederholung, Laufidentität und Beobachtung getrennt halten. Erneute Prüfung von Belegen löst keine Wiederholung eines Seiteneffekts aus. Externe Provider-Retrys bleiben im zuständigen HTTP-Profil. |
| Gym 0.26.2, `gym/core.py` 86–105 und `gym/wrappers/time_limit.py` 39–56 | Normales Ende getrennt von Unterbrechung und Zeitlimit prüfen. RL-Umgebung und Reward bleiben projektspezifisch. |
| Agent Skills, `skills-ref/src/skills_ref/parser.py` 30–64 und `validator.py` 25 ff. | Strukturdaten vor Benutzung validieren, dann fachlich auswerten. Umsetzung als gebundenes JSON-Format und Ressourcen im bestehenden Skill. Beide Uploads sind bytegleich. |
| Simple Evals, `gpqa_eval.py` 38–75 | Erwartung und beobachtetes Ergebnis unabhängig vergleichen. Der lokale Prüfer bewertet pro Schritt und meldet den Gesamtstatus ohne API-Aufruf. |
| Swarm, `swarm/core.py` 124–137 | Übergabe bezieht sich auf benannte Vorgänger und deren bestätigte Ergebnisse. Der Abgleich startet keine fremden Agenten. |
| OpenAI Agents SDK, `src/agents/run.py` 287–325 und `tool_guardrails.py` 60–109 | Laufgrenzen und unterbrochene Ausführung verhindern erfolgreiche Abnahme bei abhängigen Schritten. Bestehende Freigaben bleiben maßgeblich für echte Aktionen. |
| MLE-bench, `agents/run.py` 21–63 und getrennte `mlebench/competitions/*/grade.py` | Laufprotokoll, Artefakt und unabhängiger Vergleich bleiben getrennt. Die tatsächliche Datei wird nachgelesen. Wettbewerbsdaten, Container und der originale Grader bleiben an ihr Ursprungsprojekt gebunden. |

Die Zitate bezeichnen die gelieferten Schnappschüsse. Die Implementierung wurde für den bestehenden Coding-Profi-Lauf neu geschrieben. Sie führt keine SDK-, Container- oder Benchmark-Installation aus.
