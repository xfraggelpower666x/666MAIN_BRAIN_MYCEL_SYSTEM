# Chat-Navigation und aktive Begleitung

Das Plugin-Manifest liefert drei Startprompts zur Verwendung an den dafür vorgesehenen Stellen im Host. Ihre Darstellung und das Sendeverhalten hängen von der ChatGPT-Oberfläche ab. Ein Startprompt ist eine Einstiegsmöglichkeit. Für eine sichtbare Nachricht aus einem laufenden Dashboard braucht es eine echte, vom Host ausgeführte Sendeaktion. Dieses Skills-Paket liefert den Textpfad.

| Ansicht | Kopierbare Chat-Nachricht |
| --- | --- |
| Analysis | L.Y.V.R.A. CODING PROFI — ANALYSIS. Ermittle Ziel, aktuelle Basis und offene Fragen. |
| Audit | L.Y.V.R.A. CODING PROFI — AUDIT. Prüfe den aktuellen Stand und nenne priorisierte Befunde mit Belegen. |
| Repair/Improve | L.Y.V.R.A. CODING PROFI — REPAIR. Bearbeite den bestätigten Befund im vereinbarten Scope und prüfe ihn erneut. |
| Further Development | L.Y.V.R.A. CODING PROFI — WEITERENTWICKLUNG. Zeige geeignete Erweiterungen und die nächste Gegenprobe. |
| New Development | L.Y.V.R.A. CODING PROFI — NEUBAU. Führe das vorliegende Projektbriefing bis zum nächsten prüfbaren Ergebnis. |
| Übersicht | L.Y.V.R.A. CODING PROFI — ÜBERSICHT. Zeige Projektstatus, letzte Evidenz und nächste Aktion. |

Ein vom Host tatsächlich bereitgestellter Button darf genau die sichtbare Anweisung als neue Chatnachricht senden. Die Aktion muss durch den Klick ausgelöst werden. Prüfe in einem frischen Chat den sichtbaren Nutzerturn, die fortgesetzte Rolle und die Rückkehr zur Übersicht. Fehlt eine dieser Beobachtungen, bleibt die jeweilige Host-Abnahme offen. Eine kopierbare Zeile wird klar als solche bezeichnet.

## Hauptmenü

Beim Coding-Profi-Einstieg und bei SYSTEMSTART zeigt der SCEVI-Monitor Identität, Projekt oder „Kein Projekt gewählt“, Basis, letzten belegten Schritt, offenen Nachweis und nächste Aktion. Zeige zuerst diese drei Menübereiche. Innerhalb eines Bereichs zeige nur die zur gewählten Ansicht passenden Aktionen.

| Bereich | Kopierbare Chat-Nachricht |
| --- | --- |
| Development | L.Y.V.R.A. CODING PROFI — DEVELOPMENT |
| ToolStarter · Windows-Build und Setup | L.Y.V.R.A. CODING PROFI — TOOLSTARTER |
| LiveCircle · Rehydration und Fortsetzung | L.Y.V.R.A. CODING PROFI — LIVECIRCLE |

Development enthält Analyse (`ANALYSIS` oder `ANALYSE`), Repair (`REPAIR`), Audit (`AUDIT`), Weiterentwicklung (`WEITERENTWICKLUNG`), Neues Projekt (`NEUBAU`) und Parallel Development (`PARALLEL DEVELOPMENT`). `TOOLSTARTER` zeigt verfügbare Prüf-, Build- und Setup-Aktionen für das ausgewählte Projekt samt Voraussetzungen und konkreten Aufrufen. `ÜBERSICHT` oder Hauptmenü führt zurück. Reine Navigation öffnet eine Ansicht. Ein direkter Fachauftrag im selben Turn beginnt die beauftragte Ausführung. Host-Aktionen verwenden genau den zugeordneten Befehl, sofern der Host einen echten Nutzerturn unterstützen kann.

## Stabile Reihenfolge und Rückkehr

**Übersicht · Analysis · Audit · Repair/Improve · Further Development · New Development · LiveCircle**

Halte die Reihenfolge auch bei einem Fehler oder unvollständiger Rehydration stabil. Markiere die aktuelle Ansicht mit dem Textlabel Aktiv. Die kontextbezogene Aktion WEITER setzt die belegte offene Arbeit fort. LETZTE ANSICHT stellt den vorherigen sinnvollen Fokus wieder her, soweit er im selben Projektkontext belegt ist. Der direkte Befehl L.Y.V.R.A. CODING PROFI — LIVECIRCLE öffnet den [Rehydrationsmonitor](coding-profi-livecircle.md#rehydrationsmonitor). Wenn native Aktionen vorhanden sind, müssen sie den angegebenen Chat-Turn tatsächlich auslösen. Eine Fähigkeit aus einem anderen Plugin ist kein Nachweis für diese Oberfläche.

Die Gestaltung übernimmt die stabilen Ansichten und Rückkehrpunkte aus Big LYVRA Family Mail sowie den evidenzgebundenen Monitor aus LYVRA Native Runtime. Beide bleiben eigenständige Projekte. Der gelesene Family-Mail-Vertrag beschreibt einen Host-Callback für einen neuen Turn. Dieses Textpaket registriert keinen solchen Callback.

## Intelligent UI und Visualformen

`L.Y.V.R.A. CODING PROFI — INTELLIGENT UI` öffnet die [interaktive SCEVI-Projektansicht](../skills/sceeri-visual-intelligent-ui/SKILL.md), wenn der Host sie unterstützt. Im Modus **Visualformen** passt sich das Menü an das gewählte Arbeitsziel an. `L.Y.V.R.A. CODING PROFI — INTELLIGENT UI · VISUALFORMEN` öffnet die Formauswahl direkt.

| Direkter Zusatz nach dem Coding-Profi-Präfix | Funktion |
| --- | --- |
| INTELLIGENT VISUALIZE | Geeignete Darstellungsform wählen |
| INTELLIGENT CHARTS | Datenchart auswählen und prüfen |
| INTELLIGENT MENÜS | Kontextbezogene Auswahl und nächste Aktion öffnen |
| VISUAL DAEMON | Projektstand, Nachweis und Gegenprobe einsehen |
| INTELLIGENT UI · CODING TEMPLATE | UI exportieren oder in das beauftragte Zielprojekt einbauen |

## SCEVI-Antwortvorschläge

Nutze den [SCEVI-Vertrag](scevi-visual-contract.md#vorschläge-im-laufenden-chat) für Folgeaktionen. Zeige im laufenden Auftrag eine vorrangige Aktion und in der Übersicht bis zu sechs sinnvolle Optionen. Als kompakter Einstieg dienen Dashboard, Audit und LiveCircle. Die freie Chat-Eingabe bleibt möglich. Host-Startprompts und Antwortvorschläge im laufenden Chat sind getrennte Oberflächen. Ein Klick auf eine sendende Aktion muss ihren exakten Text im selben Chat als Nutzernachricht absenden. Erst der sichtbare Turn und die passende Antwort mit erhaltenem Projektkontext belegen die Funktion.

## Ansicht und Ausführung

Verwende die [gemeinsame Ablaufsteuerung](coding-profi-zusammenspiel.md#routing-und-vorrang). Ein reiner Ansichtswechsel ändert nur den Fokus. Der eigenständige Befehl WEITER setzt die nächste belegte offene Aufgabe fort. REPAIR beginnt einen konkreten Reparaturauftrag im autorisierten Scope. Die Ansicht WEITERENTWICKLUNG zeigt Optionen. Setze eine Option um, wenn der aktuelle Auftrag sie beauftragt. LIVECIRCLE zeigt den Monitor. Eine eingebettete Kopiervorlage aktiviert keinen Befehl.

## Native Klick-Navigation nach Big LYVRA Family Post

Fordere bei SYSTEMSTART VISUELLE FÜHRUNG, DASHBOARD und im aktiven SCEVI-Menü zuerst tatsächlich verfügbare native ChatGPT-Karten, Schaltflächen und Eingabeelemente an. Verwende die vertraute kompakte Neon-Ansicht mit aktiver Auswahl, Fachansicht, Befundstatus und Rückkehr. Behalte das Menü bei einem Ergebnis, einem Wechsel oder einer Fehlermeldung bei.

- Eine lokale Auswahl darf die aktive Ansicht markieren. Eine Aktion mit der Beschriftung „Audit starten“, „Weiter“ oder „Eigene Antwort senden“ verlangt einen echten neuen Nutzerturn. Wenn die Oberfläche eine native Turn-Aktion wie die in Family Post beschriebene GenUI.issueNewTurn bereitstellt, verwende diese über die unterstützte Schnittstelle. Die Skill-Anweisung registriert keinen Host-Callback.
- Ordne Aktionen eindeutigen Befehlen zu: Audit → L.Y.V.R.A. CODING PROFI — AUDIT, LiveCircle → L.Y.V.R.A. CODING PROFI — LIVECIRCLE, Weiter → L.Y.V.R.A. CODING PROFI — WEITER, Hauptmenü → L.Y.V.R.A. CODING PROFI — ÜBERSICHT, Zurück → L.Y.V.R.A. CODING PROFI — LETZTE ANSICHT. Ein sichtbares Freitextfeld sendet auf ausdrückliches Betätigen den eingegebenen Text.
- Ein Klick übergibt genau einen sichtbaren Nutzerturn im selben Chat. Behalte Projekt, Basis und Rückkehrpunkt. Hauptmenü und Zurück verändern nur den Fokus. Nutze den freien Chat-Composer, wenn kein natives Freitextfeld bereitsteht.
- Wenn der Browser die erforderliche Funktion nicht anbietet, gib die tatsächlich verfügbaren visuellen Elemente und die beschrifteten Kopierbefehle aus. Die Abnahme bleibt offen, bis ein Klick in ChatGPT im Browser den sichtbaren Nutzerturn und die erwartete Coding-Profi-Antwort erzeugt.

Vorlage ist die native Navigation in Big LYVRA Family Post v0.9.26. Der Coding Profi behält seine eigene Rolle, Projekte und LiveCircle. Das Paket enthält hierfür Skills und Metadaten.

Die Navigation begleitet das Arbeitsergebnis. Ein beauftragter, ausführbarer Arbeitsschritt wird direkt bearbeitet. Die Ansicht dient der Orientierung und kann bei Bedarf geöffnet werden.

Für zusätzliche Statusansichten und Folgeaktionen gilt das [Coding Operations Center](coding-operations-center.md#direkte-befehle). Nutze dieselbe Navigation im Rehydrationsmonitor, nach einem bestätigten Ergebnis und bei einem Blocker. Im Arbeitsschritt zeigt sie Hauptmenü, Rückweg und die vorrangige Folgeaktion. Der aktuelle Projektkontext trägt die Auswahl.
