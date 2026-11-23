# Intelligent UI für ein Zielprojekt

Die Vorlage enthält die Projektansicht mit Visualize, zehn auswählbare Visualformen mit Promptvorlagen, vier Chart-Ansichten und einen gemeinsamen Visual Daemon. Die Python-CLI erzeugt aus einem validierten Projekt-Datensatz eine Oberfläche mit lokalem JavaScript. Python 3.10 oder neuer genügt.

## Ausführen

```bash
python scripts/render_ui.py view.example.json intelligent-ui.html --standalone
```

Öffne die ausgegebene Datei im Browser. Für einen unterstützten Inline-Host lass `--standalone` weg, um ein HTML-Fragment zu erzeugen. Die Beispielansicht zeigt den offenen Zustand. Gib für die Integration eine Kopie von `view.example.json` mit aktuellem Projekttitel, Quellbezug, Befunden und Handlungsdaten aus dem nativen Zielsystem an.

## Einbau

- Binde den Renderer dort an, wo das Zielprojekt bereits eine bestätigte Ansicht aufbaut. Vergib eindeutige Projektkennung und native Revision in `companion.project_key` und `companion.source_revision`. Die UI verwendet ihre Daten nur für die Darstellung. Aktionen zum Kopieren liefern projektneutrale Arbeitsaufträge.
- Die Projektansicht übernimmt `narrative` und `cards` sowie schematische `line` und `bars` aus dem SCEVI-Vertrag. Für Zahlen aus einer Quelle verwende `chart` mit `intent`, `rows` und bei Bedarf `source`, `x_label`, `unit`. Die Oberfläche prüft die Datenform und zeigt bei unbrauchbaren Zahlen den nächsten Prüfschritt.
- Für Audit und Recovery übergib den aus der Fachfacette belegten Zustand in `companion`. Verwende je nach Vorliegen `phase`, `status`, `last_evidence`, `blocker`, `next_step`, `reason` und `countercheck`. Projektstatus, Schreibfreigaben und Checkpoint-Autorität verbleiben im Zielsystem.
- Gib pro Host-Container ein Fragment aus. In einem bestehenden Projekt zunächst in einem separaten Unterverzeichnis einbauen. Prüfe dessen normalen Startweg, Anzeige bei fehlender Quelle sowie lokale Navigation und Rückwege.

## Handoff und Wiederaufnahme

Die Daemon-Aktion **UI-Handoff kopieren** liefert die Ansichts-ID mit Projektkennung und Revision. Übergib das JSON an den vorhandenen Checkpoint-Ablauf und rufe den Renderer mit der bereits neu gelesenen Projektbasis auf.

```bash
python scripts/render_ui.py current-view.json intelligent-ui.html --standalone --checkpoint ui-handoff.json
```

Die Ansicht wird nur bei übereinstimmender Projektkennung und Revision übernommen. Ein ausdrücklich gewählter Startmodus aus dem aktuellen Datensatz hat Vorrang. Bei einem veralteten oder beschädigten Handoff wird der aktuelle Datensatz verwendet und der Grund auf stderr gemeldet. Fachliche Evidenz und Wiederaufnahmeaufgaben stammen aus dem verifizierten Handoff und aus den aktuellen Daten des Projekts.

**Diese Ansicht merken** speichert nur eine Darstellungspräferenz, wenn der Host Speicherzugriff erlaubt. Für zuverlässige Übergabe zwischen Hosts oder Chats nutze den UI-Handoff mit dem zugehörigen geprüften Projektcheckpoint.

## Beleggebundenes Menü

Erzeuge die optionalen `actions` aus dem fachlichen Status des Zielprojekts.
`view.example.json` zeigt einen Quellenabgleich mit einer abhängigen
Gegenprobe. Jede Aktion hat `id`, `kind` (`readback`, `clarify`, `verify`,
`navigate`), `label`, `source`, `reason`, `effect` und `countercheck`.
Optional sind `view_id`, `requires` und `status`. Sobald das Zielprojekt einen
Vorgänger mit `VERIFIZIERT` zurückliefert, kann sein Folgeschritt sichtbar
werden. Eine UI-Auswahl schreibt keinen Fachzustand. Der Daemon priorisiert
eine fachliche Sperre vor allen Vorschlägen. **Priorität merken** wirkt bei
gleichrangigen Aktionen innerhalb derselben Projektkennung und Revision.
Der UI-Handoff kann die konkrete Projektansicht mitgeben. Eigene
Startbefehle sowie Gültigkeit und Herkunft von Belegen kommen aus dem Zielprojekt.

## Plan & Ship · Abnahme im Zielprojekt

| Anforderung | Einbaupunkt | Gegenprobe |
| --- | --- | --- |
| Entscheidungsunterstützung | Datenadapter liefert belegte `actions` mit Quelle, Wirkung, Abhängigkeiten und Gegenprobe. | Zwischen zwei Ansichten wechseln und die zugehörigen belegten Vorschläge prüfen. |
| Visualformen und Zahlen | Visualize wählt die Form. Charts erhalten Werte mit Einheit und Herkunft aus der Fachquelle. | Fehlende Werte und nicht bestätigte Ursachen sichtbar offen lassen. |
| Lokales Lernen und Recovery | Die Oberfläche speichert nur die bewusst gewählte Bedienpräferenz. Das Zielprojekt führt seinen nativen LiveCircle. | Ansicht merken, neu öffnen und einen Handoff mit passender sowie abweichender Revision prüfen. |
| Oberfläche und Host | Über den normalen Einstieg des Zielprojekts einbinden. | Bedienung mit Tastatur, schmalem Fenster und blockiertem Speicher prüfen. Nachweis für echte Host-Aktionen separat erfassen. |

Im Übergabestand Ziel, native Basis, betroffene Dateien, tatsächlich ausgeführte Gegenproben, offene Aufgaben und Rückkehranker festhalten.

Für Visualformen kann derselbe Handoff optional eine Form-ID übergeben. Prüfe im Zielprojekt beispielsweise den Wechsel zu Iceberg, erneutes Öffnen und Wiederaufnahme mit passender Revision. Vorherige Formulareingaben bleiben lokal.
