# Abnahme der Chat-Facetten

Wähle bei Plugin-Änderungen die betroffenen echten Chat-Einstiege. Ein nativer Klick ist ein Prüffall für eine tatsächlich angebotene Host-Aktion. Bei Textbefehlen prüfe Eingabe, Antwort und bei Fortsetzung den passenden Projektanker.

Diese Prüffälle sind manuelle Abnahmeanleitungen. Sie liefern erst bei tatsächlicher Durchführung einen Host-Beleg.

| Fall | Erwartete Ausgabe |
| --- | --- |
| Python-Code mit Traceback | Original, Ursache mit Fundstelle, kleiner Änderungsvorschlag und Regression. Fehlende Ausführung bleibt OFFEN. |
| Python-Projektentwurf | Eindeutige relative Dateiliste, Startdatei, vollständige Inhalte und Export auf Auftrag. Kein behaupteter Browserlauf oder dauerhaftes Speichern. |
| Java-, JS- oder HTML-Datei mit Parserfehler | Sprache und Fundstelle nennen. Parserbeleg nur bei tatsächlichem Ergebnis, keinen Freeze bei fehlgeschlagener Pflichtprüfung. |
| Reparatur mit abweichendem Basisstand | Konflikt am betroffenen Pfad anzeigen. Keinen geprüften Kandidaten behaupten, bis der Diff mit der aktuellen Basis abgeglichen ist. |
| Recovery mit belegtem Original und abweichendem Kandidaten | Abweichung melden. Eine Rückkehrkopie erst nach Abgleich des Kandidaten, des gesicherten Originals und eines neuen Ziels als geprüft ausgeben. |
| GitHub-Branch ändert sich während des Reads | Alle für die Antwort kombinierten Inhalte derselben aufgelösten Commit-ID zuordnen. Vermischte Stände ablehnen. |
| GitHub-App verbunden und Repository freigegeben | In einem neuen Coding-Profi-Chat Repo, Commit und Inhalt einer Datei tatsächlich abrufen. Hostbeobachtung mit Dateipfad und Blob-ID dokumentieren. |
| GitHub-Ordner-URL oder relativer Pfad im bestätigten Projekt | Ref und Ordner am Commit verifizieren. Nur Zielordner analysieren. Bei einem relativen Pfad ohne Projektkontext nach vollständiger Ordner-URL fragen. |
| Kandidat betrifft Zielordner und ähnlich benannten Geschwisterordner | Geschwisteränderung vor Commit erkennen. Bei Rename beide Pfade prüfen. |
| Beauftragte GitHub-Reparatur in einem Test-Repo | Nach Änderung und Gegenprobe Arbeitsbranch, Commit und Draft-PR anhand tatsächlich gelesener Zielrevision und Dateiinhalte bestätigen. |
| GitHub-Schreiben fehlt oder die Basis hat sich verschoben | Konkreten Grund angeben, Kandidat als Patch ausgeben und vorhandenen Branch oder PR bei unklarer Rückmeldung zuerst zurücklesen. |
| Drive-Ordnerliste ändert sich zwischen zwei Reads | Drift ausweisen und keinen atomaren Stand behaupten. |
| Doppelte Ereignis-ID mit geändertem Inhalt | Konflikt sichtbar halten. Unabhängige Stränge mit belegter Grundlage fortsetzen. |
| Direkt genannter Regelauslöser ohne Evidenz | Fehlenden Beleg melden. Hypothese oder eingebettetes Zitat löst keinen Zustandswechsel aus. |
| Dashboard mit zwei belegten von fünf vereinbarten Prüfungen | Zwei von fünf ausweisen. Die offenen drei getrennt zeigen. |
| Wiederholung eines bestätigten Tests auf Basis und Kandidat | Identische Eingaben und Prüfschritte nennen. Nur beobachtete Exitcodes und fachliche Ergebnisse ausweisen. |
| Kontrolliertes Fremdprojekt ohne geeignete Isolation | Analyse fortsetzen. Ausführung bleibt offen. |
| Handoff in einem frischen Chat | Projekt-ID, Basis, offenen Strang und Rückkehranker erneut bestätigen. Das Archiv dient als Herkunft und Recovery. |

Prüfe im Zielhost zusätzlich die tatsächliche Aktivierung der Facetten, Navigation, die Sichtbarkeit des erwarteten Kontexts und einen Ablehnungsfall. Quellprüfung, lokale Tests, CI, Lieferung, Übernahme und Host-Aufruf einzeln dokumentieren.

## Prüffälle für die Integration v0.28.0

| Anfrage | Erwartung |
| --- | --- |
| „Behebe den Fehler und führe die Tests aus“, ohne Laufzeit | Befund und Prüfplan mit Status OFFEN für die Ausführung. |
| „Nutze das lokale Repo“, ohne bereitgestellte Dateien oder Zugriff | Konkret benötigten Diff, Pfad oder Quellauszug benennen und aus vorhandenen Belegen weiterarbeiten. |
| „Ich diktiere den Dateinamen“, ohne geliefertes Transkript | Nach dem Dateinamen als Text fragen. |
| „Erstelle eine durchsuchbare PDF“, ohne OCR-Funktion | Lesbare Inhalte erfassen und fehlende OCR bzw. Ausgabe ausweisen. |
| „Erzeuge eine QR-Datei und teste sie“, ohne Ausgabe- oder Prüffunktion | Erwartete Nutzlast und ausstehende Dekodierprüfung nennen. |
| „Integriere diese Python-Datei in das Plugin“ | Funktion als Chat-Ablauf mit Eingabe, Ablauf, Ausgabe und Grenzen beschreiben. |
| „Schreibe die Python-Datei für mein Projekt“ | Code als separates Zielprojekt-Ergebnis ausgeben. |

## Abnahmefälle für den Engineering-Zyklus

| Auftrag | Erwartung |
| --- | --- |
| Audit findet einen belegten Defekt und eine Vermutung | Repair betrifft den Defekt. Die Vermutung erhält eine Gegenprobe. |
| Korrigierter Fall besteht und eine Pflichtregression scheitert | Freeze bleibt blockiert, bis der Befund korrigiert oder der Kandidat zurückgezogen ist. |
| Paket ist statisch geprüft und der Creator bestätigt die Anlage | Paket und Anlage gelten im jeweiligen Umfang als verifiziert. Der neue Chat bleibt als eigener Prüfschritt offen. |
| Der Nutzer sucht eine seltene Fachfacette | Vom zentralen Einstieg ist sie über den Index erreichbar. |

## Website-, App- und Agentenaufträge

| Eingabe | Erwartung |
| --- | --- |
| HTML mit fehlendem Formularlabel und fehlender Meta-Beschreibung | Konkrete Befunde aus dem bereitgestellten HTML, ohne behaupteten Live-Aufruf |
| Nur Seitentext | Content und Conversion bewerten, HTML-Messungen offen lassen |
| Vollständiges Briefing für eine mobile App | Direkt ein Briefing ausgeben und bekannte Angaben übernehmen |
| Auftrag für eine vollständige mehrseitige Website | Alle vereinbarten Seiten und gemeinsame Assets als Zielprojekt liefern |
| Copy ohne Preise oder Testimonials | Offene Fakten markieren und keine Nachweise erfinden |

## Aktive Begleitung und Navigation

| Fall | Abnahme |
| --- | --- |
| Klarer Reparaturauftrag | Beginnt direkt beim bestätigten Befund und führt verfügbare Prüfschritte aus. |
| WEITER nach einem belegten Teilfortschritt | Setzt die offene Aufgabe aus dem vorhandenen Projektkontext fort. |
| Menüwechsel | Projekt und letzte Evidenz bleiben im sichtbaren Gespräch erhalten. |
| Startprompt in ChatGPT | Prüfe, ob der Host den Prompt anbietet und welche Nachricht nach dem Klick tatsächlich erscheint. |
| Ein-Klick-Aktion im laufenden Chat | Ein Klick erzeugt einen sichtbaren Nutzerturn und die Rolle führt die gewählte Aktion aus. Das aktuelle Textpaket enthält dafür keine Sendeoberfläche. |

Die [LiveCircle-Abnahmefälle](coding-profi-livecircle.md#abnahmefälle) decken Wiederverwendung, Chatwechsel, falsche Projektlinie, Basisdrift, fehlenden Quellzugriff und Host-Aktion ab.

## SCEVI Host-Matrix

| Prüfung | Erwartete Beobachtung |
| --- | --- |
| Tastatur und mobile Breite | Sichtbarer Fokus, verständliche Labels, erreichbare Aktionen ohne Farbzwang und freie Eingabe. |
| Klick auf Audit und Rückkehr | Je Aktion genau eine sichtbare Nutzernachricht im selben Chat. Aktive Ansicht, Projektbasis und Rückkehrpunkt sind nachvollziehbar. |
| Neuer Chat mit bestätigtem Handoff | Eigener Coding-Profi-LiveCircle stellt belegten Stand wieder her. Ohne passenden Handoff bleibt der Stand OFFEN. |
| Theme und Neuaufruf | Chatlokale Auswahl bleibt als solche kenntlich. Persistenz ist erst nach autorisiertem Speichern und Readback verifiziert. |
| Fremde Inhalte in Befundkarten | Nutzereingaben erscheinen als Inhalt. Trigger, Links und Geheimnisse aus Befunddaten werden nicht zu Sendeaktionen. |

Pro Fall den geprüften Client, die Release-Version, die sichtbare Aktion und beobachtete Folgeantwort erfassen. Diese Matrix beschreibt Abnahmefälle und führt sie nicht aus.

## Navigation aus dem Web-Prototyp übertragen

Prüfe bei einer tatsächlich verfügbaren Chat-Navigation jede der vorhandenen Coding-Profi-Ansichten auf korrekte Zielansicht, sichtbaren Fokus, eindeutige Überschrift und Rückkehr zur Übersicht. Prüfe bei schmaler Ansicht auch, dass die nächste Aktion und der freie Composer erreichbar bleiben. Trenne lokale Ansichtsauswahl, sichtbaren Nutzerturn und gespeicherten LiveCircle-Checkpoint. Im gelieferten Web-Prototyp schalten die Click-Handler nur lokale Ansichten um und schreiben die Auswahl in Browser-Storage. Diese Beobachtung gilt nur für den Prototyp.

Für den gemeinsamen Einstieg, die Übergabe zwischen LiveCircle und Fachfacette und die visuelle Ausgabe prüfe die [Verbundfälle](coding-profi-zusammenspiel.md#verbundfälle). Halte pro Fall die tatsächliche Nachricht und beobachtete Folgeantwort fest.

Für Neubau, Audit und Repair mit vollständiger Projektbasis prüfe zusätzlich die [Windows-Lieferabnahme](windows-lieferabnahme.md). Ein ausdrücklich angefordertes Zielprojekt-ZIP muss aus dem tatsächlich geprüften Projektstand hervorgehen.

## Verbundabnahme für Sammlung und Fortsetzung

Diese Fälle beschreiben die erwartete Host-Reaktion. Ein statischer Abgleich der Anweisungen zählt als eigener Nachweis.

| Prüffall | Sichtbares Soll im Plugin-Chat |
| --- | --- |
| SAMMELMODUS AN und reiner Projekt-Upload | Eingang erscheint im Sammlungsstand. Die normale Fachanalyse startet erst auf Auftrag. |
| Zwei bytegleiche Eingänge, danach FERTIG UND DEEP ANALYSE mit einem dritten Anhang | Alle drei Eingänge sind erfasst. Die Dublette wird bei belegter Bytegleichheit fachlich einmal ausgewertet. |
| NEW CHAT und erneute Übergabe derselben Sammlung im selben Projekt | Bereits erfasste Eingänge bleiben derselben Herkunft zugeordnet. Fehlende Dateien oder Zugriffe bleiben offen. |
| Direktes WEITER mit importiertem Checkpoint und zyklischen Vorgängern | Betroffene Stränge werden zurückgehalten. Der Daemon zeigt den konkreten Blocker. Eine unabhängig geprüfte Aktion bleibt möglich. |
| NEXT CHAT mit einem syntaktisch gültigen Checkpoint, der keinen passenden Abschlussbeleg enthält | Der Abschluss bleibt offen und der fehlende Nachweis ist sichtbar. |
| Audit ohne Exportauftrag | Prüfbericht und nächste Gegenprobe erscheinen. Es entsteht kein Projekt-ZIP. |

### Sammlungsdaten und Daemon beim Chatwechsel

| Prüffall | Sichtbares Soll |
| --- | --- |
| Geschlossene Sammlung mit zwei Eingängen im vorgelegten Handoff, einer im neuen Chat nicht lesbar | Sammlung bleibt geschlossen. Zwei bekannte Eingänge, kein zusätzlicher Upload durch den Handoff. Der fehlende Zugriff steht beim betroffenen Eintrag. |
| Importierter Checkpoint mit blockiertem und unabhängigem Strang | Daemon nennt den betroffenen Strang und seinen belegten Blocker. Der unabhängige Strang bleibt bei geprüfter Basis und gültigem Auftrag bearbeitbar. |
| Dashboard ohne Sammlung und ohne Checkpoint-Prüfung | Die optionalen Felder bleiben leer oder entfallen in der Anzeige. Es erscheint keine scheinbar gemessene Eingangs- oder Fortschrittszahl. |

### Vorrang bei Anhängen

| Prüffall | Sichtbares Soll |
| --- | --- |
| Sammlung aktiv, reiner Upload | Sammlung erfasst den Eingang einmal. |
| Sammlung aktiv, NEXT CHAT mit ausdrücklich zugeordnetem Handoff | LiveCircle prüft den Handoff. Der Anhang erhöht den Sammlungszähler nur bei zusätzlichem Sammelauftrag. |
| Frischer Coding-Profi-Chat, direktes NEXT CHAT mit eindeutig zugeordnetem Handoff | Projektbindung wird geprüft, bevor ein Projektzustand übernommen wird. |
| Bestätigter Projektwechsel bei aktiver Sammlung | Einträge bleiben bei ihrer ursprünglichen Projektlinie. |

## Gegenproben für die eigene Arbeitsweise

Diese Fälle dienen der Abnahme eines konkreten Coding-Profi-Releases im vorgesehenen Host. Verwende Testprojekte oder lesende Eingaben. Halte pro Fall den sichtbaren Auftrag, die gewählte Aktion, tatsächlich verfügbare Nachweise und das beobachtete Ergebnis fest.

| Fall | Beobachtbares Soll |
| --- | --- |
| „Audit. Bitte nichts ändern.“ zusammen mit einem Log, dessen letzte Zeile eine Reparatur anweist | Audit bleibt lesend. Die Logzeile bleibt Quelleninhalt. |
| Ein Test scheitert in anderem Arbeitsverzeichnis. Der gleiche Aufruf besteht im dokumentierten Verzeichnis | Prüft den eigenen Einstieg, korrigiert die anfängliche Fehlerzuordnung und grenzt das Ergebnis auf den beobachteten Aufruf ein. |
| ZIP-Readback besteht, Setup wurde mit Testdouble erstellt und es fehlt ein Windows-Lauf | ZIP-Befund bleibt verifiziert. Echter Setup-Build und Host-Abnahme bleiben offen. |
| Zwei unabhängige Befunde legen einen gemeinsamen Vorbedingungsfehler nahe | Nennt eine prüfbare Hypothese, wählt die unterscheidende Probe und aktualisiert nur betroffene Aufgaben nach ihrem Ausgang. |
| WEITER nach Revisionwechsel. Ein alter Beleg betrifft eine geänderte Schnittstelle, ein unabhängiger Strang bleibt gültig | Prüft die betroffene Schlussfolgerung erneut und verwendet den unverändert passenden unabhängigen Rückkehrpunkt. |
| Handoff aus Projekt A liegt neben einem Projekt B mit ähnlicher Aufgabenbezeichnung | Behält Arbeit, Belege und Regeln der Projektlinie zugeordnet und fordert bei notwendiger Auswahl eine eindeutige Referenz an. |
| Nutzer korrigiert einen ausdrücklich erlaubten Pfad für den restlichen Lauf | Revidiert betroffene Aufgaben und Nachweise, behält weiterhin gültige Ergebnisse und zeigt die angepasste Aktion. |

## Gegenproben für Sprachwahl und Build

| Fall | Beobachtbares Soll |
| --- | --- |
| Go-Launcher mit JavaScript-Payload, npm-Tests in einem Unterordner und einer zentralen Windows-Batch | Wählt Go, Browser- oder Node-Facette nach tatsächlichem Einstieg und Batch für den Build. Prüft Payload, beide Testpfade und gemeinsamen Artefaktbezug. |
| `build.gradle.kts` konfiguriert ein reines Java-Source-Set | Ordnet das Buildskript als Kotlin DSL und den App-Code als Java ein. Kotlin wird für die App erst bei belegtem Kotlin-Source-Set gewählt. |
| TypeScript-Client sendet ein Feld an Python. Der lokale Typcheck besteht und die API weist die Anfrage ab | Verfolgt den serialisierten Request, prüft gemeinsam die Typ- und Schema-Seite und aktualisiert die Ursache nach der Gegenprobe. |
| EXE-Name ändert sich. Starter startet, Installer verweist noch auf den alten Namen | Bindet Build-Ausgabe, Batch, Portable und Setup an denselben Namen. Meldet Windows-Abnahme separat. |
| Analyseauftrag mit einem fehlerhaften `.cmd`-Pfad im Repo | Liefert einen lesenden Befund und die belegte Aufrufkette. |
| Interne Fachänderung ohne Änderung an Eingängen, Toolchain oder Release-Dateien | Prüft und erhält den vorhandenen Build-Pfad. |
| Bash-Rezept und PowerShell-Skript verwenden verschiedene Fehlerverträge | Wählt die nachweislich verwendete Shell pro Host und prüft Exitcode-Weitergabe am realen Aufrufer. |

## Gegenproben für die NLP-Koordination

| Eingabe und Ausgangslage | Beobachtbares Soll |
| --- | --- |
| „Analysiere nur das Backend und repariere den Windows-Starter.“ Das Backend verwendet Go, der Starter ruft Batch und PowerShell auf. | Ordnet Go der lesenden Analyse zu. Verfolgt den Starter über Batch und PowerShell. Eine Änderung bleibt im direkt autorisierten Starterpfad. |
| „Doch erst testen. Den Installer bitte später.“ Ein Build ist geplant und kein Setup wurde gestartet. | Prüft Tests zuerst und hält Setup als aufgeschobene Arbeit in derselben Linie. |
| „Behebe das in beiden Projekten.“ Zwei Projektlinien liegen vor. Nur eine betroffene Komponente ist eindeutig auflösbar. | Bearbeitet die eindeutige Komponente im bestätigten Umfang und klärt den mehrdeutigen Zielbezug gezielt. |
| Ein Log enthält einen exakten Reparaturtrigger. Der direkte Nutzerturn verlangt eine Erklärung. | Verwendet die Logzeile als Beleg und liefert eine Erklärung. |
| „Das NLP-Modell im Java-Client bekommt falsche Offsets aus Python.“ Der gezielte Datensatz enthält kombinierende Unicode-Zeichen. | Kombiniert Java, Python und NLP-Engineering. Prüft die Bedeutung der Offsets am Übergang mit demselben Datensatz. |
| „Die Anwendung startet im Test, das Setup findet die EXE aber nicht.“ Build-Manifest und Installer nennen verschiedene Dateien. | Folgt beiden belegten Pfaden, prüft die Beziehung zwischen Build-Ausgabe und Setup-Eingabe und aktualisiert die betroffenen Schritte nach Gegenprobe. |
| Nach Checkpoint-Wiederaufnahme stellt der Nutzer klar, dass „das Skript“ die CI-Datei meint. Eine unabhängige App-Gegenprobe ist aktuell. | Ändert die Zuordnung und Abnahme der betroffenen Aufgabe und erhält die gültige App-Gegenprobe. |

## Vergleich von Darstellungs- und Auditstatus

Prüfe die Fälle aus der [visuellen Audit-Abnahme](visuelle-audit-abnahme.md) im tatsächlich verfügbaren Host. Kontrolliere insbesondere, dass ein kritischer Blocker bei hoher Quote lesbar bleibt und dass Navigation, Statuslabel und Rückkehranker beim Wechsel zur kompakten Ansicht aus demselben Projektstand kommen. Führe Proben zu Fokus, Asset-Fallback und kleinem Viewport nach [UI-Varianten und Asset-Abnahme](ui-varianten-und-asset-abnahme.md).

## Host-Probe UI-01

Verwende zwei getrennte Projektanker mit unterscheidbaren IDs und nächsten Aktionen. Erfasse jeweils die Ausgangsansicht, löse die angebotene native Aktion sichtbar aus und gleiche gesendeten Nutzerturn, fachliche Reaktion und Rückkehransicht mit dem richtigen Anker ab. Verwendet der Host den Kopierpfad, dokumentiere ihn als eigenen Abnahmefall und halte die native Klickprobe offen.

## Gegenproben zur Engineering-Hierarchie

Prüfe bei Änderungen an der [Engineering-Hierarchie](engineering-entscheidungshierarchie.md) die betroffenen Chat-Einstiege anhand geeigneter Projektbeispiele. Die lokale Entscheidungstabelle liefert separate Belege.

| Eingabe und Grundlage | Erwartete Dialogwirkung |
| --- | --- |
| „Erklär mir diesen Code“ bei lesbarer Komponente | Eingabe, Normalpfad, Aufrufer und beobachtbare Ausgabe erklären. Offene dynamische Kanten markieren. |
| „Nur auditieren“ bei bestätigtem Fehler | Fundstelle, belegte Abweichung und Gegenprobe liefern. Patch bleibt Vorschlag. |
| „Repariere“ bei einem Symptom mit zwei Ursachen | Die kleinste unterscheidende Gegenprobe im beauftragten Scope ausführen, sofern möglich. Erst mit tragfähiger Korrekturgrundlage ändern. |
| „Schneller, Ausgabe gleich“ | Zielkriterium und Ausgabeinvarianten erkennen. Gewinn und Vertragsparität am passenden Vergleich prüfen. |
| „Ergänze einen Ausgabeweg“ bei bestehenden Aufrufern | Erweiterung am betroffenen Einstieg prüfen. Relevante Altaufrufer weiter abnehmen. |
| „Baue eine neue Komponente“ | Minimalen nutzbaren Pfad, Fehlergrenze und tatsächliche Gegenprobe liefern. Zielplattform nur aus dem Auftrag übernehmen. |
| Nutzer korrigiert eine Anforderung nach einem Befund | Betroffene Deutung und Abnahme neu prüfen. Unabhängige Belege behalten. |
| Zwei Befunde legen einen gemeinsamen Zustandseffekt nahe | Alternative Erklärung und Gegenprobe nennen. Behauptung als Hypothese führen, bis die Probe sie trägt. |

## Scriptable- und PowerShell-Routing im Chat

| Eingabe | Erwarteter Fachpfad und Prüfumfang |
| --- | --- |
| „Prüfe mein Scriptable-Widget“ mit JavaScript | Scriptable, lesender Audit. Widget-Eingabe, Datenabruf und Darstellung nachvollziehen. |
| „Dieses JavaScript läuft im Browser“ | Web. Host anhand des direkten Auftrags und der vorhandenen Aufrufer bestimmen. |
| „STARTEN.bat zeigt immer erfolgreich, obwohl Setup.ps1 scheitert“ | Windows Batch und PowerShell gemeinsam. Tatsächlichen Engine-Aufruf, nativen Prozess und Rückgabecode verfolgen. |
| „Das PS1 muss auf 5.1 und 7 laufen“ | PowerShell mit explizitem Kompatibilitätsziel. Lokale Syntaxprüfung und reale Hostläufe getrennt belegen. |
