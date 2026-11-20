# Datenvertrag für die wiederholbare UI

Der Renderer nimmt UTF-8-JSON. Er erzeugt ein einzelnes HTML-Fragment mit eingebetteten Styles und lokalem JavaScript. Die JSON-Daten werden validiert und als Text in den Fragment-Datensatz eingefügt; Ansichten verwenden `textContent`. Keine Netzwerkaufrufe, keine Projektmutation, keine Sendeaktion.

```json
{
  "title": "Projekt · Ansicht",
  "subtitle": "Kurzbeschreibung",
  "basis": "konkrete Datei, Revision oder Nutzerangabe",
  "views": [
    {
      "id": "overview",
      "title": "Übersicht",
      "summary": "Was ist hier sichtbar?",
      "kind": "narrative",
      "route_terms": ["übersicht", "bild"],
      "source": "konkreter Quellverweis",
      "status": "VERIFIZIERT",
      "items": [
        {"label": "Beobachtung", "text": "Nur abgelesene Angabe"}
      ]
    }
  ],
  "gaps": ["Was trotz der Quelle offen bleibt"]
}
```

Pflicht: `title`, `basis`, ein bis sechs `views`. Jede Ansicht benötigt eindeutige ASCII-ID, Titel, Kurzbeschreibung, Typ, mindestens einen Suchbegriff, konkrete Quelle und Status. Die Typen:

- `narrative` und `cards`: `items` mit `label` und `text`. Keine leeren oder erfundenen Fakten.
- `line`: ein oder zwei `series` mit `label` und zwei bis 32 normierten `values` im Bereich 0–100. Gleich viele Punkte. Nur `data_kind: "schematic"`; Status `ABGELEITET`; verpflichtende `caption` mit „qualitativ“. Diese Zahlen sind Layoutkoordinaten und erscheinen nicht als gemessene Werte.
- `bars`: zwei bis zwölf `bars` mit `label` und `level` 0–100. Nur `data_kind: "schematic"`; Status `ABGELEITET`; `caption` enthält „qualitativ“. Keine Werteachse.

Die UI zeigt Quelle und Status der gewählten Ansicht; globale `gaps` bleiben sichtbar. Ein Treffer schaltet lokal um. Zwei Treffer erzeugen OFFEN mit Auswahlmöglichkeit; ohne Treffer ebenso. Ein Klick in der UI ist keine Chatnachricht.

Für einen Screenshot kann man die vier sichtbaren Module als Ansichten verwenden. Titel und 142 BPM sind ablesbar; lange Prompttexte und genaue Kurvenwerte aus einem sehr kleinen Bild bleiben OFFEN. Das Beispiel ist kein Current Pointer für irgendein Projekt.


## Optionale Begleitdaten

- `companion` kann `phase`, `status`, `last_evidence`, `blocker`, `next_step`, `reason` und `countercheck` enthalten. Übernimm die Werte aus derselben belegten Projektbasis. Fehlt ein konkreter Beleg, bleibt er offen. `start_mode` kann `project`, `formats` oder `charts` sein und hat Vorrang vor einer Vorliebe. Gib `project_key` und `source_revision` aus dem nativen Projekt an, wenn die Ansicht später rehydriert werden soll.
- `chart` erwartet `intent` mit `compare`, `trend`, `relationship` oder `composition` sowie `rows` als Text. Format je Zeile für Verlauf, Vergleich und Anteile ist `Bezeichnung;Wert`, für Zusammenhang `X;Y`. Dezimalkomma und Dezimalpunkt werden unterstützt. Fehlende Werte bleiben offen. `source`, `unit`, `x_label` sind optional. Der Daemon unterscheidet vorliegende Nutzerdaten, offene Quellprüfung und eine aus diesen Zahlen erzeugte Darstellung.
- UI-Handoff `scevi.visual.handoff.1` enthält `project_key`, `source_revision` und `mode`. Der Renderer akzeptiert ihn über `--checkpoint` erst bei passender Projektkennung und Revision. Das Projekt muss zuvor anhand der nativen Autorität geprüft sein.
- `handoff_format` wählt `coding-profi` oder `neutral`. Der projektneutrale Export nutzt `neutral` als Standard. In jeweils einem Host-Container darf ein Fragment stehen.

Beispielaufruf für ein eigenständiges HTML-Dokument: `python3 scripts/render_ui.py input.json output.html --standalone`. Ohne Schalter entsteht ein Inline-Fragment. Für das übertragbare Coding-Template gilt die [Einbauanleitung](../template/README.md).

## Beleggebundene Aktionsvorschläge

`actions` ist optional und enthält bis zu acht Einträge. Jeder Eintrag hat
eine ASCII-ID (`id`), `kind` aus `readback`, `clarify`, `verify`, `navigate`,
sowie `label`, `source`, `reason`, `effect` und `countercheck`.
Optional binden `view_id` an eine vorhandene Ansicht und `requires` an
andere Aktions-IDs. `status` ist `VORGESCHLAGEN` (Standard),
`VERIFIZIERT` oder `BLOCKIERT`. Nur vorgeschlagene, zur Ansicht passende
Aktionen mit vollständig verifizierten Vorgängern erscheinen als Auswahl.
Unbekannte Vorgänger und Zyklen werden vor der Darstellung gemeldet.
Der freigegebene Datensatz gehört dem Projekt. Ein Klick zeigt Folge,
Quelle und Gegenprobe. Er bestätigt keinen Schritt im Projektzustand.

Schreibkonflikt, fehlender Readback oder ein Blocker aus Projekt oder
aktiver Ansicht haben Vorrang vor dem Menü. Eine explizit gemerkte Aktion
wird bei gleicher fachlicher Priorität für die Projektkennung und Revision
bevorzugt. Der Browser speichert die Aktions-ID und löscht beschädigte
Präferenzen aus dem betreffenden Schlüssel. Bei Speicherfehler gilt die
Vorliebe vorübergehend in der offenen Ansicht.

Der kompatible UI-Handoff kann außerdem `view_id` enthalten. Damit
stellt die Rehydration die konkrete Projektansicht auch nach einem
Wechsel in Charts oder Visualformen wieder her. Ein fachlich vorgegebener
`companion.start_view` hat Vorrang. Frühere Handoffs mit Modus allein
bleiben gültig.

Im Modus `formats` kann `companion.start_format` eine Form-ID wählen, etwa `iceberg` oder `decision-matrix`. Ein passender UI-Handoff kann optional `format_id` liefern. Eine ausdrückliche Startform hat Vorrang. Das Menü prüft seine verfügbaren Formen und bleibt bei einer entfallenen Form benutzbar.
