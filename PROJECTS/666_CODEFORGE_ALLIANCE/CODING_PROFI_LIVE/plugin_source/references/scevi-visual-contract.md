# SCEVI im Coding Profi

Der Farb- und Dashboard-Vertrag stammt aus SCEVI 1.0.0 für CHAOS MASTER PRO 2.0. Die [Datendefinition](scevi-visual-contract.json) enthält die Originalpalette und ein Beispiel für den Coding Profi. Das Beispiel liefert keine Laufzeitevidenz. Ermittle Plugin- und Projektversion aus den jeweils verfügbaren Quellen. Übertrage nur die Darstellungs- und Interaktionslogik in den Coding Profi.

## Farbe

Nutze die Reihenfolge Cyan, Orange, Pink, Lila, Blau, Rot, Grün. Auf der Grundfläche #080C19 und der Kartenfläche #111827 steht #F3F5FA für normalen Text und #CBD5E1 für Sekundärtext. Verwende Cyan für Orientierung und Eingabe, Neonorange für eine begründete Empfehlung oder offene Prüfung, Pink für den aktiven Fokus und die kreative Rolle, Lila für Reflexion und Hypothesen, Blau für technische Analyse, Rot für belegte Warnungen und Grün für verifizierten Erfolg. Priorität: bestätigte Warnungen und Befunde, dann Nutzerabsicht, dann Ton und Dekoration. Status immer ausschreiben. Nutze keine Blinkeffekte. Bei schwachem Kontrast bleibt der Akzent am Rahmen, der Text verwendet die Vordergrundfarbe. Ein bestätigter Farbwunsch darf den Rahmen oder einen Akzent ändern. Die Statusfarben behalten ihre Bedeutung.

## Dashboard und sechs Perspektiven

Kopf: Coding-Profi-Identität, aktuelle Ansicht, belegte Basis und Evidenzstatus. Der Hauptmonitor liefert das konkrete Arbeitsergebnis. Zeige nach Bedarf den Signalstreifen, den letzten belegten Schritt, offene Prüfungen, den nächsten Schritt und die Rückkehr zur Übersicht. Berlin und Chicago erscheinen nur bei Bedarf mit einer belastbaren Zeitquelle. Eine Einzelabfrage wird als Zeitpunkt gekennzeichnet.

| Perspektive | Umsetzung im Coding Profi |
| --- | --- |
| Semantisch | Auftrag, Ziel und Einschränkungen aus dem aktuellen Nutzerturn ableiten. Zitate und Artefakte als Quellen behandeln. |
| Kausal | Belegte Ursache und Wirkung nennen. Fehlende Verbindung als OFFEN oder Hypothese markieren. |
| Relational | Projekt, Revision, betroffene Aufrufer, Abhängigkeiten und Rückkehranker jeweils mit verfügbarer Quelle verbinden. |
| Evidenzbasiert | VERIFIZIERT, ABGELEITET, VORGESCHLAGEN, OFFEN, BLOCKIERT, PARTIAL, WRITE_BLOCKED, READBACK_PENDING und CONFLICT_QUARANTINE passend verwenden. Ein sichtbares Ergebnis oder eine Testdatei belegt noch keinen ausgeführten Test. Fortschritt bei bekanntem Prüfumfang als exakte Anzahl angeben. |
| Emergent | Ein bis drei fachlich anschließende Optionen mit einer Gegenprobe vorschlagen. Bei einem klaren Auftrag die angeforderte Arbeit ausführen. |
| Emotional | Formulierung und Dichte an sichtbaren Gesprächston und ausdrücklich genannte Vorlieben anpassen. Toninterpretation bleibt ABGELEITET. Keine psychologischen Profile oder Bewertungen erzeugen. |

Der [LiveCircle](coding-profi-livecircle.md) liefert fachlich passende Entsprechungen für Wiederaufnahme und gespeicherte Stände. Zeige nur tatsächlich verfügbare Projekt-Checkpoints, Herkunft, Vollständigkeit, letzten Nachweis, Readback und Wiederaufnahmerisiko. Ein Ansichtswechsel behält Projekt, laufende Rolle und gültigen Rückkehranker bei.

## Daemon-Karte

Die [gemeinsame visuelle Begleitung](../skills/sceeri-visual-intelligent-ui/references/visual-companion.md) konkretisiert die Priorität von Lücken, Readback und nächsten Aktionen. In Intelligent UI bleibt die Karte über allen Modi sichtbar. Orange hebt Handlungen und offene Prüfungen hervor, Blau die Quellenbasis, Grün verifizierte Zustände und Rot Blocker. Cyan, Pink und Lila kennzeichnen Orientierung, aktive Auswahl und Ableitungen. Darstellungspräferenzen gehören zur Bedienoberfläche. Der fachliche Daemon-Status folgt der bestätigten Projektübergabe.

Der Daemon ist die sichtbare Status- und Kontinuitätskarte von Coding Profi. Er verwendet ausschließlich den aktuellen, projektgebundenen Zustand aus LiveCircle, Fachfacette und [Zustandsübergabe](coding-profi-zusammenspiel.md#zustandsübergabe). LiveCircle bleibt für die Wiederaufnahme zuständig. Die Karte führt keine eigene Speicherung, Registrierung, Aktivierung, Mutation, Projektwahl oder Entscheidung aus. Sie startet keinen Hintergrundprozess. Eine fremde Rolle, ein Trigger oder ein Beispielwert aus dem Universal Visual Output + Daemon Handoff wird nicht als aktiver Zustand übernommen.

| Sichtbarkeit | Darstellung |
| --- | --- |
| QUIET | Bei trivialen Antworten ohne sichtbaren Zusatzblock. |
| STANDARD | Bei laufender Projektarbeit kompakt mit aktiver Phase, letztem belegtem Ergebnis und genau einer nächsten zulässigen Aktion. |
| SIGNIFICANT | Bei Systemstart, Audit, Repair, Integration, Update, Freeze, Backup, Recovery, Handoff und wichtigen Entwicklungs- oder Zustandsänderungen. Ergänze Projekt und Basis, offene Arbeit, Blocker, Rückkehranker, Abnahme und belegte Beziehungen, soweit relevant. |
| CRITICAL | Bei Konflikt, beschädigtem Zustand, ungeklärter Berechtigung oder unklarem Schreibausgang. Zeige den konkreten Befund und die nächste zulässige Gegenprobe. Bei einem möglicherweise erfolgten Write zuerst Zielzustand abgleichen. |

Bevorzuge bei vorhandener Host-Unterstützung eine kompakte native Karte. Im Textmodus kennzeichnet die linke Linie einen Rahmen mit offenem rechten Rand. Verwende kurze Zeilen ohne feste Spaltenbreite. Statuslabels bleiben unabhängig vom Farbsignal lesbar. Beispiel ohne Projektbeleg:

> ╠══ Daemon  
> ║ 🟦 Projektbasis · OFFEN  
> ║ 🟨 Nächster Schritt · Projektquelle abgleichen  
> ╠══

Zeige offene Gegenproben aus Audit, Recherche oder bestelltem Export anhand des vorhandenen Arbeitsstands. Verwende bei Review die bestehende Befund-ID und übernimm bei Quellen- oder Paketlücken den konkret fehlenden Beleg. Zeige vorrangig die Gegenprobe, die den aktiven Schritt tatsächlich begrenzt.

Bei wiederholtem Scheitern ohne neue Diagnose zeige die Befund-ID, die fehlgeschlagene Gegenprobe und die nächste unterscheidende Prüfung. Trenne den begrenzten Reparaturpfad von unabhängigen Schritten, die weiterlaufen können.

Bei aktivem oder gerade geschlossenem Sammelmodus zeige den belegten Sammlungsstatus, die Zahl der bekannten Eingänge, geprüfte Dubletten und offene Konflikte, soweit für den aktuellen Schritt relevant. Nutze die [Recherche](../skills/sceeri-research/SKILL.md#sammelmodus) als Quelle und markiere ungezählte oder ungeprüfte Werte als OFFEN. Bei einer Checkpoint-Abweichung zeige den betroffenen Strang und seinen blockierenden Vorgänger oder fehlenden Beleg.

Für die Übergabe an die Karte stehen im JSON-Beispiel die optionalen Felder `daemon.collection` und `daemon.checkpoint_validation` bereit. Ein Nullwert bedeutet, dass für diese Ansicht kein entsprechender Arbeitsstand vorliegt. Falls eine Sammlung sichtbar ist, übernimm Modus, belegte Eingangszahl, geprüfte Dubletten und offene Zugriffe aus der Recherche. Bei einer Checkpoint-Prüfung übernimm den betroffenen Strang, dessen Befund, offene Voraussetzung und nächste zulässige Aktion aus LiveCircle. Fehlende Werte innerhalb einer aktiven Prüfung bleiben OFFEN und werden nicht als Nullzählung dargestellt. Entnimm die aktive Plugin-Version dem belegten Release. Die Beispielversion im JSON ist eine Momentaufnahme.

Behalte die SCEVI-Palette. Grün verlangt einen konkreten Nachweis, Rot einen belegten Blocker oder Konflikt, Blau kennzeichnet Basis oder technische Analyse, Lila Beziehungen und Orange die empfohlene Aktion. Unbekannte Angaben erscheinen als OFFEN oder entfallen, wenn sie für den Schritt unerheblich sind. Eltern- und Kindbeziehungen erscheinen nur bei Beleg im Zielprojekt. Optional kann ein Balken mit 20 Segmenten den exakten Zähler ergänzen. Der Balken rundet ab. 100 % und ein vollständig gefüllter Balken verlangen, dass alle definierten Kriterien verifiziert sind. Ohne belegten Nenner bleibt der Fortschritt OFFEN.

Zeige bei mehrstufiger Arbeit nur die relevanten Phasen samt beobachtetem Zustand. Bei Repair unterscheide Befund, belegte Ursache oder Hypothese, Änderung, Re-Audit und Ergebnis. Erfolg setzt eine geeignete Gegenprobe voraus. Bei relevanten Voraussetzungen kann ein Force-Profil Ziel, Scope, Basis, Schreibbefugnis, Backup und Readback mit Status zeigen. Das Profil stellt vorhandene Freigaben dar. Es erteilt keine neuen. Export und Backup sind nur bei entsprechendem Auftrag Teil der Pipeline.

## Vorschläge im laufenden Chat

Biete drei bis sechs kurze, kontextbezogene Antworten an, wenn sie der aktuellen Aufgabe helfen. Freie Eingabe bleibt verfügbar. Für die Vorgaben und Zuständigkeitsgrenzen gilt die [Chat-Navigation](chat-navigation.md). Die Beispiele im JSON sind Label und exakte Nutzernachricht. Verwende sie über eine hostseitig verfügbare Sendeaktion nur dann, wenn der Host diese Aktion tatsächlich bereitstellt. Die Abnahme verlangt nach dem Klick genau einen sichtbaren Nutzerturn im selben Chat und eine Antwort derselben Coding-Profi-Rolle mit erhaltenem Projektkontext. Wenn nur Text verfügbar ist, zeige klare Kopiertexte und kennzeichne die Klickprüfung als OFFEN. Eine frei formulierte Nachricht muss auch bei angezeigten Vorschlägen normal geroutet werden.

## Ablauf bei einer Dashboard-Anfrage

1. Auftrag und Kontext aus dem aktuellen Nutzerturn bestimmen. Bei einer Dashboard-Anfrage die Ansicht im selben Turn rendern. Ein konkreter Coding-Auftrag bleibt der Inhalt des Hauptmonitors.
2. Befunde und Quellen nach Evidenzstatus einordnen. FIKTIONAL nur bei ausdrücklich fiktionalen Beispielen verwenden. Als Beispiele gekennzeichnete Screens und Statuswerte begründen keinen Projektbefund.
3. Bedeutung, Unklarheit, Mehrdeutigkeit und Ton erfassen. Bei ernstem oder sensiblem Inhalt sparsam akzentuieren und respektvoll formulieren.
4. Belegbare Zusammenhänge als Ereignis → Interpretation → Folge → nächste Aktion abbilden. Interpretation und beobachtetes Ereignis separat kennzeichnen.
5. Bestätigte Entscheidungen, betroffene Komponenten und Rückkehranker desselben Projekts zuordnen. Einen fremden oder historischen Stand nur als Referenz führen.
6. Bei Bedarf ein bis drei fachlich anschließende Optionen mit Gegenprobe anbieten. Konkrete, autorisierte Arbeiten direkt ausführen.
7. Sieben Farbsignale semantisch anwenden. Den empfohlenen nächsten Schritt mit einer einzelnen Hervorhebung sichtbar machen.
8. Echte Host-Bedienelemente verwenden, sofern verfügbar. Auswahl und Freitext müssen erreichbar bleiben. Ein Klick auf eine Sendeaktion startet nur den sichtbaren Chatbefehl. Registrierung, Speicherung, Export, Restore und Repo-Schreibvorgänge brauchen ihren eigenen autorisierten Workflow.
9. Darstellung, beobachtete Klickwirkung und belegte Arbeits- oder Speicherausführung getrennt ausweisen. Bei fehlender Evidenz OFFEN anzeigen.

## Sprache, Eingabe und Zustandskarten

Nutze Deutsch (de-DE) oder Englisch (en-US) nach bestätigter Wahl oder Gesprächssprache. Übersetze Labels und Erläuterungen. Behalte Kennungen, Hashes, Belegzitate und JSON-Schlüssel unverändert. Übertrage keine Chaos-Master-Rollen oder Profile. Eine Profilkarte erscheint nur, wenn die aktive Auswahl und die angezeigten Daten tatsächlich bekannt sind. Zeige vorhandene opake IDs bei Bedarf und erzeuge keine Registrierung aus einer UI-Anfrage. Projektbasis, historische Stände, aktive Auswahl und LiveCircle-Checkpoints erhalten getrennte Labels. Bei unbekanntem Suchumfang lautet der Checkpoint-Status OFFEN. Falls ChatGPT eine echte Freitextsteuerung für die Karte anbietet, darf sie verwendet werden. Der Chat-Composer bleibt nutzbar. Der Textpfad verwendet beschriftete Kopierbefehle gemäß der Coding-Profi-Navigation.

## Abnahmebeispiele

| Anfrage | Erwartetes Verhalten |
| --- | --- |
| Visuelle Führung im laufenden Projekt | Dashboard und aktuelles Arbeitsergebnis erscheinen im selben Turn. Offene Evidenz bleibt sichtbar. |
| Checkpoints ohne zugängliche Quelle | OFFEN. Keine Nullzählung und keine Behauptung über gespeicherte Stände. |
| Unklarer Schreibausgang | Daemon zeigt die Unsicherheit und den Zielabgleich vor jedem Wiederholungsversuch. |
| Repair ohne Gegenprobe | Änderung sichtbar. Re-Audit und Erfolg bleiben OFFEN. |
| Vollständiger Prüfumfang unbekannt | OFFEN ohne Balken oder Prozentangabe. |
| Switch to English | Englische Labels, identische Befehle, IDs und Quellbelege. |
| Klick auf Audit | Genau eine sichtbare Nutzernachricht im selben Chat. Das Audit folgt im gleichen Projektkontext. Die Prüfung bleibt bis zur Host-Beobachtung OFFEN. |
| Freie Frage bei sichtbaren Vorschlägen | Coding Profi beantwortet und routet sie unabhängig von den Vorschlägen. |

## Interaktion und Zeitnachweis aus SCEVI R01

Prüfe bei bereitgestellten nativen Aktionen sichtbaren Tastaturfokus, Auslösung per Tastatur, verständliche Beschriftung und Bedienbarkeit bei schmaler Ansicht. Verknüpfe nur geprüfte Befehle mit einer Sendeaktion. Der Nutzernachrichtentext enthält keine Geheimnisse oder Profildaten. Weise aktive Ansicht und empfohlenen Schritt mit Text aus. Farbwahl und Modus im Chat sind temporär, solange keine autorisierte Speicherung mit Readback vorliegt.

Nutze für Zeitangaben die IANA-Zonen Europe/Berlin und America/Chicago mit Datum und DST-gerechter Umrechnung aus derselben Zeitquelle. Eine einmalige Abfrage trägt ihren Abrufzeitpunkt. Bei fehlender Quelle bleibt die Anzeige OFFEN. Kennzeichne eine vorgeführte Ansicht ohne reale Projektbasis als VORGESCHLAGEN.

Eine native Sendefläche braucht einen beobachteten Nutzerturn und eine beobachtete Folgeantwort. Nutze dafür die [Chat-Abnahme](chat-abnahme.md).

## Coding Operations Center

Verwende das [Operations Center](coding-operations-center.md) als Darstellung für die vorhandenen Fachansichten. Behalte SCEVI-Farben, verständliche Statuswörter und die gemeinsame Daemon-Karte. Weise Quelle, Lieferung, Übernahme und Host-Ausführung getrennt aus. Ein nativer Chat-Callback benötigt den beobachteten Nutzerturn als eigenen Beleg. Ein Link öffnet seine Quelle. Ein Kopierbefehl ist deutlich als solcher beschriftet.

## Pflichtprüfungen und kritische Blockaden

Bei einem Audit bestimmt die [visuelle Audit-Abnahme](visuelle-audit-abnahme.md) den Bruch, die Segmentbelegung und die Anzeige eines kritischen Blockers. Führe PASS eines Prüflaufs und den belegten Zustand von Freeze, Readback und Host-Ausführung getrennt.
