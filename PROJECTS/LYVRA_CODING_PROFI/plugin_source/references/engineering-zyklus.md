# Engineering-Zyklus für mehrstufige Aufträge

Wende die Phasen an, die der Nutzer für das benannte Projekt beauftragt. Bewahre Basis, bisherige Fähigkeiten und geprüfte Ergebnisse. Halte pro Phase den Scope, den beobachteten Befund, die Änderung oder Entscheidung, die Gegenprobe und die nächste Aktion fest. Für Ausführung und Rückfallwege gilt das [Chat-Betriebsmodell](chat-betriebsmodell.md).

| Phase | Arbeit | Abnahme |
| --- | --- | --- |
| Verstehen | Normalpfad, Aufrufer, Daten, Zustände und Verträge aus dem bestätigten Scope erfassen | Beobachtung, Quellmechanismus und Hypothese mit Fundstellen trennen |
| Audit | Basis, gewünschtes Verhalten, Fehler oder Lücke, betroffene Aufrufer und Erhaltungsvorgaben erfassen | Befunde mit Quelle, Status und Priorität |
| Repair | Kleinste Änderung für einen belegten Befund entwerfen oder autorisiert durchführen | Diff oder geänderte Dateien und dieselbe Gegenprobe auf Basis und Kandidat, soweit verfügbar |
| Re-Audit | Korrektur und benachbarte Funktionen prüfen | Jeder ursprüngliche Befund behält seine [Befund-ID](../skills/sceeri-code-review-and-refactor/SKILL.md#befundverfolgung) und hat Ergebnis, offene Gegenprobe oder verbleibenden Blocker |
| Verbesserung | Benanntes Kriterium verbessern und bestehende fachliche Verträge erhalten | Basis und Kandidat mit passender Gegenprobe vergleichen |
| Neubau | Beauftragtes neues System oder Komponente am minimalen Normalpfad aufbauen | Vertrag für Eingabe, Ausgabe und Fehlerverhalten tatsächlich prüfen, soweit ausführbar |
| Weiterentwicklung | Ergänzung aus Auftrag oder Audit mit messbarem Ziel umsetzen | Abgrenzung, erwartetes Verhalten und Beobachtung des normalen Einstiegspunkts |
| Abschlussaudit | Inhalt, Links, Metadaten, relevante Regressionen, Auswirkungen und ausstehende Prüfungen erfassen | Abnahme pro Ebene mit konkreter Quelle oder beobachtetem Ergebnis |

## Phasenauswahl und Integration

Die [Engineering-Hierarchie](engineering-entscheidungshierarchie.md) bestimmt fachlichen Einstieg und Kriterien pro beauftragtem Teilziel. Nutze bei einem gemischten Auftrag den Scope jedes Teilziels.

Für mehrstufige Projektarbeit verwende die [Ablaufsteuerung](build-control.md#entscheidung-vor-der-ausführung) für die Ausführungsentscheidung, Validierung und gegebenenfalls begrenzte Reparatur. Wenn im Auftrag eine Freigabe enthalten ist, prüfe den tatsächlichen Kandidaten mit der [Freigabeprüfung](build-control.md#freigabeprüfung). Das fachliche Ergebnis bleibt an den vorhandenen Projektablauf und dessen Belege gebunden.

Direkte Aufträge zu Integration, Audit, Repair, Freeze, Systemsicherung, Backup, Paketierung oder ZIP nutzen diesen Zyklus mit der jeweils beauftragten Wirkung. Ein reines AUDIT prüft lesend und liefert Vorschläge. REPAIR oder FIX umfasst die gezielte Korrektur und Re-Audit im bestätigten Scope. FREEZE prüft die Freigabekriterien. Systemsicherung, Backup oder Paketierung bestimmen ausdrücklich den Sicherungs- oder Exportumfang. Reine Analyse, ein Anhang oder ein zitierter Trigger erteilt keine Schreib-, Veröffentlichungs- oder Exportberechtigung. Bei einem kombinierten Auftrag arbeite in fachlicher Reihenfolge.

Bei einer Integration sichere die Originalbasis im erlaubten Zielbereich. Ordne eingespeiste Anforderungen bestehenden Funktionen zu. Ordne Lücken und Überlappungen der vorhandenen Zuständigkeit zu. Bei Fremdcode gilt der nachfolgende Ablauf auch für bestehende, beauftragt weiterzuentwickelnde Funktionen. Bei einem Prompt-System forme geeignete Codefragmente in überprüfbare Regeln, Eingaben und Ausgabe-Verträge um. Auditiere Vollständigkeit, Widersprüche, Guards, Doppelzuständigkeiten, Authority, Ausgabe, Scope, Readback, Freeze und Artefaktinventar. Repariere bestätigte Abweichungen und prüfe den Kandidaten erneut. Halte Anforderungen, Befunde, Reparaturen und Gegenproben rückverfolgbar.

## Fremdcode im aktiven Architektur- und Codebau

1. **Quellbasis und Deep Audit.** Inventarisiere alle relevanten Eingaben mit Herkunft und Revision oder Archivhash. Prüfe den echten Quellcode, Build-Verträge, Abhängigkeiten, Tests und Lizenzhinweise. Verfolge den Mechanismus von Einstieg und Eingaben über Schnittstellen, Zustände und Aufrufer bis zu Ausgabe und Seiteneffekten. Erfasse Voraussetzungen, Reihenfolge, implizite Invarianten, Fehlerpfade und relevante Wechselwirkungen. Fundstellen und beobachtete Ergebnisse tragen unterschiedliche Aussagen. Weise unbekannte Laufzeitpfade als offen aus.
2. **Idee übernehmen und anpassen.** Ordne für jeden wesentlichen Mechanismus die beabsichtigte Wirkung, die tragenden Kausalbeziehungen und die passende Zuständigkeit in der Zielarchitektur zu. Entwickle die Idee mit den vorhandenen Zielverträgen weiter und implementiere sie in der Sprache und Struktur des Zielprojekts. Bei mehreren Quellen prüfe, welche Mechanismen sich ergänzen oder miteinander kollidieren. Leite einen neuen Ansatz aus belegten Zusammenhängen ab, formuliere die erwartete Wirkung und prüfe sie. Umfang eines Diffs ist zweitrangig gegenüber der fachlichen Vollständigkeit. Erhalte jede für die Wirkung notwendige Beziehung oder belege funktionale Gleichwertigkeit im normalen Pfad, Fehlerpfad und bei betroffenen Bestandsaufrufern.
3. **Quellcode nur als notwendige Ausnahme.** Übernimm Fremdcode nur, wenn ein konkret belegter technischer Grund die zielnative Umsetzung für den Umfang unzureichend macht. Dokumentiere benötigten Ausschnitt, Grund, Herkunft, Lizenz und erforderliche Hinweise. Bei unklarer Übernahmegrundlage bleibt der Kopierpfad offen. Eine fachlich geeignete eigene Implementierung kann im genehmigten Umfang fortgesetzt werden.
4. **Real einbauen und nachweisen.** Bei einem beauftragten Einbau implementiere, registriere und verdrahte die Änderung am vorgesehenen Einstieg mit echten Schnittstellen und Verbrauchern. Liefere den Diff oder die geänderten Dateien. Prüfe den Ablauf vom Einstieg bis zur beobachteten Wirkung oder zum Ergebnis, einschließlich berührter Fehler- und Regressionpfade. Ein Auditauftrag allein bleibt lesend. Ist die Implementierung oder Laufzeitprüfung blockiert, benenne exakt den fehlenden Zugriff, die fehlende Umgebung oder den betroffenen Pfad. Ein Konzept, eine isolierte Demo, eine importierte Datei oder ein erfolgreicher Build allein belegt keine aktive Integration.
5. **Abdeckung und Übergabe.** Führe je relevanter Idee die Kette **Quelle/Fundstelle → Mechanismus und notwendige Beziehungen → Zielpfad und Patch → Gegenprobe und Ergebnis**. Kennzeichne Ideen als umgesetzt, teilweise umgesetzt, offen oder fachlich verworfen und begründe jede Abweichung. Eine Probe muss einen Verlust der entscheidenden Beziehung erkennen können. Bei fehlendem Laufzeitbeleg kennzeichne die konkrete Prüfung als offen.

## Altverhalten und Gegenprobe

Halte bei Änderungen an bestehendem Verhalten vor dem Patch die betroffenen normalen Einstiege, öffentlichen Schnittstellen und relevanten Grenzfälle fest. Erfasse je Fall Eingabe, erwartetes Ergebnis, Basisrevision und beobachteten Ist-Stand oder offene Prüfung. Bezeichne den beabsichtigten Verhaltenswechsel ausdrücklich. Verwende für die zu erhaltenden Fälle dieselbe Gegenprobe an Basis und Kandidat, soweit ausführbar. Unerwartete Abweichungen erhalten einen Befund mit Auswirkung und Nachweis. Prüfe bei vorhandenen Release-Metadaten auch [Abweichungen zwischen den aktiven Trägern](../skills/sceeri-evidence-parity/SKILL.md#drift-in-release-metadaten).

Nutze bei Änderungen des Quellstands die [gezielte Nachprüfung](../skills/sceeri-repository-intelligence/SKILL.md#gezielte-nachprüfung-nach-quelländerungen). Prüfe vor dem Abschlussaudit, ob der tatsächliche Prüfumfang das Ergebnis trägt. Nenne verbleibende Lücken und Konflikte mit ihren betroffenen Befund-IDs.

## Freeze

Identifiziere Artefakt, Version, Inhalt und, wenn gemessen, SHA-256. Bei ausdrücklich beauftragter Paketierung lies das gepackte Ergebnis erneut und vergleiche es mit dem geprüften Kandidaten. Wenn eine im Auftrag erforderliche Prüfung fehlschlägt, sperre die Freigabe und nenne den konkreten Befund. Eine statisch geprüfte Chat-Ausgabe darf als solche eingefroren werden, wenn die praktische Host-Abnahme als offen ausgewiesen ist. Verwende historische Testergebnisse nur für ihren ursprünglichen Stand.

Wenn der Nutzer den Creator beauftragt, prüfe den eigenen Eintrag anhand der tatsächlichen Identität. Verwende den eingefrorenen Stand für eine private Anlage oder den passenden Update-Weg. Belege die Anlage über die Creator-Antwort und überprüfe, soweit möglich, Version, sichtbare Dateien und Freigabestatus. Unterscheide Readback im Creator von einem Aufruf in einem frischen Chat.

Der eingefrorene Stand ist die geschützte Referenz für die laufende Operation. Offene materielle Befunde und fehlende Pflichtnachweise blockieren den Freeze der betroffenen Ebene. Ändere den eingefrorenen Stand innerhalb der Operation nicht. Eine beauftragte Sicherung liest den Kandidaten und erstellt ein separates Lieferartefakt. Halte bei dateibasierter Lieferung Versionsstand, Changelog, Manifest und SHA-256-Inventar fest.

## Systemsicherung und ZIP

Bei bestellter Systemsicherung liefere die im Scope verfügbare Originalbasis, den integrierten Stand, Auditbericht, Repair-Log, Freeze-Status und ein Manifest mit Herkunft, Pfaden, Dateigrößen und SHA-256-Prüfsummen. Kennzeichne redigierte, unzugängliche oder anderweitig nicht lieferbare Quellen und dokumentiere ihre sichere Wiederbeschaffung. Entferne Zugangsdaten aus allen Lieferdateien. Packe eine bestellte mehrteilige Exportsicherung als ZIP. Prüfe nach Erstellung die Integrität, die erwarteten Pfade und die Hashes des Archivlesefunds gegen das Inventar. Ein Manifest kann sich nicht selbst hashen. Ein separater Hash des gesamten Archivs kann zusätzlich die übergebene ZIP-Datei identifizieren. Richte Lieferprofile und explizite Exportgrenzen am [Projektabschluss](code-delivery.md#verbindlicher-projektabschluss) aus.

## Lieferprüfung am normalen Projekteinstieg

Bei konkretem Neubau, Projekt-Audit oder Verbesserung wende den [Projektabschluss](code-delivery.md#verbindlicher-projektabschluss) an. Prüfe den Windows-Starter vor dem Abschlussaudit, wenn er zum beauftragten Zielprojekt gehört. Bestätige bei Freeze den geprüften Stand. Prüfe ein Zielprojekt-ZIP bei ausdrücklich beauftragtem Export. Halte fehlende Quellen, Plattform und fehlgeschlagene Pflichtprüfungen pro Ebene fest.

Prüfe die [Projektsprachen](../skills/sceeri-projektsprachen/SKILL.md) bereits am Ausgangsstand und erneut am Lieferkandidaten. Bei einem reinen Audit bleiben Änderungen Vorschläge. Beim beauftragten Repair gehen die Korrekturen in die Arbeitskopie.

Führe bereits beauftragte aufeinanderfolgende Phasen ohne erneute Menüwahl aus. Wenn die Umgebung eine konkrete Phase blockiert, arbeite an zulässigen unabhängigen Schritten weiter und nenne den fehlenden Nachweis. Nutze die [Prozessführung](../skills/sceeri-coding-profi-chat/SKILL.md#prozessführung-im-laufenden-auftrag).

Bei vorgeschlagenen oder beauftragten CodeForge-Kandidaten und Archivprüfungen verwende die [Coding-Workflows](coding-workflows.md) für Pfadabdeckung, Snapshots, Prüferwahl und getrennte Restore-/Readback-Belege. Bei einem Prozess- oder Tool-Handoff aus einem anderen Projekt nutze die [Aufnahmeentscheidung](coding-workflows.md#tool-vorschläge), bevor du eine neue Implementierung planst.

Bei System- oder Modulintegration prüfe im Abschlussaudit [Modulaudit und Funktionsschutz](build-control.md#modulaudit-und-funktionsschutz). Wenn ein einsatzbereiter Handoff beauftragt ist, prüfe auch die [Handoff-Abnahme](build-control.md#handoff-abnahme).

[Architekturaudit v0.74.0](architekturaudit-074.md) führt Befunde und Architekturänderungen dieser Hierarchie.
