---
name: sceeri-scevi-visual-intelligence
description: Render SCEERI audits and project evidence as SCEVI dashboards; use the Intelligent UI skill for requested interactive visual guidance in supported ChatGPT hosts.
---

# SCEVI für SCEERI Code Engineering

Nutze diesen Skill bei einer ausdrücklich angeforderten visuellen Führung, einem SCEERI-Dashboard oder beim visuellen Aufbereiten eines vorliegenden Engineering-Berichts. Identität und Ausführungsbefugnis bleiben bei SCEERI und dem betroffenen Projekt.

1. **Semantik.** Benenne den konkreten Auftrag und den erfassten Quellstand. Bei einem vorhandenen Bericht verwende dessen Schema und Felder.
2. **Evidenz.** Trenne gemessene Parserdiagnosen, blockierte Dateien, Patch-Kandidaten und tatsächlich ausgeführte Gates. Zeige fehlende Berichte oder Prüfphasen als OFFEN. Ein existierender Patch ist VORGESCHLAGEN, auch nach bestandenem Freeze.
3. **Kausalität.** Zeige den ersten belegten Abbruchpunkt und seine Auswirkung. Ohne Nachweis bleibt die Ursache eine Hypothese.
4. **Relationen.** Ordne Baseline und Kandidat getrennt zu. Verknüpfe geänderte Dateien, Gate-Ergebnisse und Recovery-Originale nur über vorhandene Daten und Hashes.
5. **Emergenz.** Schlage höchstens drei nächste Prüfungen vor, etwa die erste fehlende Regression oder die Prüfung eines Diffs. Vorschläge lösen keinen Lauf aus.
6. **Darstellung.** Verwende die kanonische Reihenfolge und Rollen aus dem [SCEVI-Vertrag](../../references/scevi-visual-contract.md#farbe). Pink markiert Fokus und kreative Rolle, Neonorange die begründete Empfehlung oder offene Prüfung. Kombiniere jede Farbe mit einem Textlabel.

Rendere die angeforderte Ansicht direkt im Chat. Verwende native Karten, Auswahl oder Fortschrittsanzeigen, wenn der Host diese tatsächlich bereitstellt. Für den Textpfad nutze barrierearmes Markdown. Stelle Status, Beleg, nächsten Schritt und Rückkehrpunkt kompakt dar. Verwende vorhandene Host-Bedienelemente nur bei tatsächlicher Unterstützung. Zeige sensible Rohdaten nur im benötigten, zulässigen Umfang.

Chaos-Master-Profile, Rollenmodi und Spielstände gehören zur Quellreferenz. Für SCEERI sind Quellstände, Evidenz, Kandidaten und Recovery die entsprechenden Ansichten. Diese Darstellung veranlasst weder eine Systemaktivierung noch Dateischreibzugriffe.

Bei einem Handoff-Plan (`sceeri-handoff-plan-v1`) zeige Rückkehranker, betroffene Stränge, Konflikte und offene Pflichten. Kennzeichne die Welle als Vorschlag. Der lokale Markdown-Renderer zeigt die erfassten Anzahlen und den Gesamtstatus. Einzelbefunde bleiben im JSON-Bericht.

Zeige bei einer belegten Kursänderung die ausschlaggebende Beobachtung, den zugehörigen Beleg und die tatsächlich aktualisierte nächste Aktion aus der [Entscheidungs- und Lernschleife](../../references/coding-profi-zusammenspiel.md#entscheidungs--und-lernschleife). Halte die Darstellung bei unverändertem Arbeitsstand kompakt.

## Mermaid-Auswahl

Nutze Flowcharts für Verzweigungen, Sequenzen für Nachrichtenreihenfolge, Zustandsdiagramme für Übergänge, ERD für Datenbeziehungen und Gantt für Zeitplanung mit belegten Abhängigkeiten. Verwende wenige Elemente, klare Beschriftungen und zum Host passende Syntax. Bezeichne einen Entwurf als solchen, wenn die Darstellung nicht gerendert geprüft wurde.

## Farb- und Nachweisreferenz

Auf dunkler Fläche können Cyan #00F5FF, Orange #FFAD58, Pink #FF1493, Lila #BA55FF, Blau #247CFF, Rot #FF244A und Grün #39FF14 als Akzente dienen. Verwende ausgeschriebene Statuslabels, ausreichenden Kontrast und keine blinkenden Effekte. Zähle beobachtete Prüfungen gegenüber ausdrücklich definierten Prüfungen. Zeige je Strang Phase, letzten belegten Schritt, Blocker und nächste Aktion. Bei fehlenden Werten bleibt die Angabe offen.

## Feste Navigation und Rehydrationsmonitor

Nutze auf den Ansichten dieselbe Reihenfolge und markiere den Fokus lesbar. Pink zeigt die aktive Ansicht, Cyan die Orientierung und Lila Beziehungen oder Kontinuität. Verwende kompakte native Chat-Blöcke und auf kleinen Bildschirmen kurze Beschriftungen. Zeige zuletzt belegten Schritt, nächsten Schritt und offenen Nachweis. Verlinke den [Rehydrationsmonitor](../../references/coding-profi-livecircle.md#rehydrationsmonitor). Navigation und erfolgreiche Host-Aktion erhalten getrennte Belege.

## SCEVI-Referenz für Dashboard und Chat-Aktionen

Nutze den [SCEVI-Vertrag](../../references/scevi-visual-contract.md) für die sechs Perspektiven, Farbsignale und kontextbezogenen Antwortvorschläge. Aktualisiere die sichtbaren Perspektiven aus dem belegten Projektstand. Wenn der Host echte Sendeaktionen anbietet, verwende für ausgewählte Vorschläge die genaue Nachricht. Bei reinem Text gilt die beschriftete Kopieroption aus der Chat-Navigation.

## Arbeitsreihenfolge und Sprachwechsel

Wende die [SCEVI-Arbeitsreihenfolge](../../references/scevi-visual-contract.md#ablauf-bei-einer-dashboard-anfrage) bei jeder angeforderten visuellen Führung an. Verwende die bestätigte Sprache (DE/EN) für Labels. Verweise für Checkpoint- und Wiederaufnahme-Evidenz auf den eigenen Coding-Profi-LiveCircle. Benenne die Phase und liefere das aktuelle fachliche Ergebnis im Hauptmonitor.

Nutze beim Agentenlauf die [Zustandsübergabe](../../references/coding-profi-zusammenspiel.md#zustandsübergabe) als Quelle für Ansicht, Evidenz und Rückkehrpunkt. Übernimm die Ergebnisdaten aus Fachfacette und LiveCircle. Die Anzeige löst selbst keine Wiederaufnahme aus.

Nutze bei Dashboard und visueller Führung zuerst die [native Klick-Navigation](../../references/chat-navigation.md#native-klick-navigation-nach-big-lyvra-family-post). Erhalte die Aktionen nach jeder relevanten Antwort. Ein echter Sendeklick und eine lokale Ansichtsauswahl haben unterschiedliche Wirkung.

Zeige die [Daemon-Karte](../../references/scevi-visual-contract.md#daemon-karte) als Standard für operative Statusausgaben. Nutze die passende Sichtbarkeit. Ergänze bei bedeutenden oder kritischen Operationen den belegten Daemon-Status auch ohne gesonderte Dashboard-Anfrage. Fasse die nächste Aktion einmal zusammen. Das fachliche Ergebnis bleibt sichtbar.

Beim Coding-Profi-Einstieg rendere den LiveCircle-Stand mit [Hauptmenü](../../references/chat-navigation.md#hauptmenü). Für Parallel Development zeige nur beobachtete Läufe als aktiv. Eine nachweisbare Abhängigkeit, ein konkurrierender Write oder ein offener Readback erklärt den Blocker. Stelle bei einer neuen Erkenntnis die veränderte Entscheidung mit Beleg, Wirkung und Gegenprobe dar. Offene Hypothesen werden als solche markiert.

## Evidenz in Entscheidungen und Vorschauen

Verwende [Evidenz und Interaktion](../../references/scevi-evidenz-und-interaktion.md) bei widersprüchlichen Signalen, Trenddarstellung, relevanten Entscheidungs-Gates oder einer beauftragten interaktiven Vorschau. Prüfe Baseline und Nachweise vor einer visuellen Konsistenzreparatur.

## Audit-Entscheidung und Balken

Verwende bei relevanten Audits die [visuelle Audit-Abnahme](../../references/visuelle-audit-abnahme.md). Setze die Statusentscheidung aus dem beauftragten Prüfumfang vor die Zahlenanzeige. Wenn ein lokaler Python-Host bereitsteht, kann der dort verlinkte Audit-Rechner den Bruch, die Segmente und die blockierenden Prüf-IDs ausgeben. Die Daemon-Karte verweist bei einem Blocker auf die konkrete Gegenprobe.
## Zehn Visualformen für Erklärungen und Entscheidungen

Verwende für Entscheidungsführung, Datencharts und UI den [gemeinsamen Visual Daemon](../sceeri-visual-daemon/SKILL.md). [Intelligent Visualize](../sceeri-intelligent-visualize/SKILL.md) wählt die passende Fachform, [Intelligent Charts](../sceeri-intelligent-charts/SKILL.md) verwendet Zahlen, und [Intelligent Menüs](../sceeri-intelligent-menus/SKILL.md) zeigt den nächsten Schritt aus derselben Basis.

Wähle bei einem ausdrücklichen Formwunsch die gleichnamige Fachfacette; sonst nutze die [Auswahl und Evidenz](../../references/visual-formats.md). Jede Form behält die SCEVI-Statuslogik und die native Autorität des betroffenen Projekts. Präzise Fakten, Relationen, Termine und Raster werden vor der Gestaltung gegen die Eingabe geprüft. Formen: [Handwritten](../sceeri-visual-handwritten/SKILL.md), [Sketch Notes](../sceeri-visual-sketch-notes/SKILL.md), [Decision Matrix](../sceeri-visual-decision-matrix/SKILL.md), [Infographic](../sceeri-visual-infographic/SKILL.md), [Canvas](../sceeri-visual-canvas/SKILL.md), [Layers](../sceeri-visual-layers/SKILL.md), [Cycle](../sceeri-visual-cycle/SKILL.md), [Diagramm](../sceeri-visual-diagramm/SKILL.md), [Roadmap](../sceeri-visual-roadmap/SKILL.md) und [Iceberg](../sceeri-visual-iceberg/SKILL.md).


## Wiederholbare interaktive Ansicht

Bei einer direkt angeforderten „Intelligent UI“, „Visualize“ oder interaktiven visuellen Führung nutze [Intelligent UI](../sceeri-visual-intelligent-ui/SKILL.md). Verwende dessen validierten Renderer und aktuelle Projektbelege. Eine lokal interaktive Ansicht sendet keinen Chat-Turn; fehlende Host-Unterstützung führt zum beschrifteten Textpfad. Das fachliche Ergebnis und der LiveCircle bleiben die Autorität.

