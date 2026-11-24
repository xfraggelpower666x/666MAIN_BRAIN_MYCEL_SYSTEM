# SCEVI bei Entscheidungen und interaktiver Darstellung

Verwende die bestehende Palette und Navigation. Wähle pro Auftrag die kleinste Darstellung, die Fortschritt, Blocker oder eine Entscheidung verständlich macht.

## Zustand und Nachweis

| Feld | Anzeige |
| --- | --- |
| Objekt und Basis | Konkreter Lauf, Strang, Schnittstelle oder Artefakt mit Revision oder Fingerabdruck. |
| Beobachtung | Was beobachtet, gemessen oder aus bekannten Eingaben berechnet wurde. Bei Schätzung, Schlussfolgerung oder Prognose die Methode und den Status angeben. |
| Beziehung und Wirkung | Betroffener Vertrag, Aufrufer und konkrete beobachtete oder erwartete Wirkung. |
| Zeit und Drift | Bei vergleichbarer Basis den Zeitraum und beobachteten Trend angeben. Wenn die Basis abweicht, die Gültigkeit der älteren Evidenz vor einer Trendaussage prüfen. |
| Entscheidung und Aktion | Entscheidergebnis, Grund, nächste zulässige Aktion und deren eigener Ausführungsbeleg. Eine Warnung oder Kartenwahl verleiht keine weiteren Rechte. |

Zeige widersprüchliche Dimensionen nebeneinander. Auch bei bestandenen Tests bleibt beispielsweise ein fehlender Host-Readback offen. Bei unbekanntem Nenner oder nicht vergleichbaren Messungen entfällt der Balken. Bei vergleichbaren Prüfungen ist der Zähler maßgeblich. Prognosen und Handlungsoptionen bleiben als solche markiert. Farben und Ansichtswechsel verändern weder Nachweis noch Projektzustand.

## Darstellungswahl

- Revisionsvergleich oder Abnahmestatus: kompakte Markdown-Tabelle. Abhängigkeitskette mit aussagekräftigen Verzweigungen: Mermaid mit Textalternative.
- Auswahl mit Beobachtung und Rückkehr: vorhandene native Auswahl nutzen, wenn sie der Host bereitstellt. Lokale Auswahl, gesendeter Nutzerturn und ausgeführte Projektaktion sind getrennt abnehmbar. Beim Textpfad kopierbare Aktionen anbieten.
- Bei beauftragter interaktiver Vorschau das gleiche Zustandsmodell nutzen. Zeige Status und Blocker unabhängig von der Farbe, beschrifte Eingaben, prüfe Tastaturfokus und schmale Ansichten. Eine Browser-Vorschau bekommt eine eigene Abnahme. Bedienelemente zeigen ihre beobachtete Wirkung und simulierte Daten werden als Beispieldaten gekennzeichnet.
- Bei visueller Reparatur prüfe dieselben Zustandsfelder vor und nach Darstellung oder Ansichtswechsel. Identität, Revision, offene Prüfung und Rückkehrpunkt müssen aus demselben bestätigten Datensatz stammen.

Gegenproben: fehlender Nenner, widersprüchliche Statusdimensionen, veraltete Revision, lokale Auswahl ohne Sendefunktion und Wechsel vom Dashboard zum fachlichen Ergebnis mit erhaltenem Rückkehrpunkt.

## Vergleich mehrerer visueller Zustände

Für Theme, Viewport oder Ansichtsvarianten verwende [UI-Varianten und Asset-Abnahme](ui-varianten-und-asset-abnahme.md). Vergleiche explizite Invarianten und erlaubte Abweichungen vor einem visuellen Repair. Beobachte bei einer nativen Chat-Aktion zusätzlich die gesendete Nachricht und die daraus folgende Projektansicht.
