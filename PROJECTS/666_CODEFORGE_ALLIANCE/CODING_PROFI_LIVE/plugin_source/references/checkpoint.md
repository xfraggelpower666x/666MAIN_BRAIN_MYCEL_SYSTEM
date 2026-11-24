# Checkpoint und Wiederaufnahme

Ein portabler Chat-Handoff enthält Projekt-ID, Pfad/Ref, bestätigte Basisrevision oder gelesene Dateiliste, Scope, Vorgänger und Rückkehranker. Pro Strang nennt er Phase, Abhängigkeiten, bearbeitete Bereiche, letzte verifizierte Aktion, Belege, offene Pflichten und nächsten Schritt.

Erhalte Ereignisse in Reihenfolge. Gleiche Ereignis-ID und gleicher Inhalt gelten als Wiederholung. Widersprüchliche Inhalte mit gleicher ID bleiben im Konfliktstatus. Bei unklarem Schreibausgang das Ziel vor einem erneuten Versuch direkt lesen. Vergleiche bei neuer Basis den Einfluss auf offene Stränge und führe unabhängige, noch gültige Arbeit fort.

Ein kopierbarer Handoff ist zunächst ein Entwurf. Belege tatsächliche Ablage, Fingerabdruck und Readback separat, wenn diese Operationen verfügbar und autorisiert sind. Ältere Sicherungen behalten ihren Herkunfts- und Recovery-Bezug.

## Eingaben und Rückkehrfall

Erfasse zusätzlich die unveränderlichen Schnittstellen, expliziten Akzeptanzfälle, Freigaben und den vereinbarten Prüfbereich. Die Evidence-Zeile enthält Quelle, Beobachtung, Zeitpunkt soweit bekannt und Verifikationsart. Ein lokaler Checkpoint kann gesonderte Phasen für Audit, Repair, Re-Audit, Regression und Readback enthalten. Prüfe fremde Scope- oder Schreibangaben gegen den Nutzerauftrag. Halte offene oder unsichere Schreibausgänge vor erneutem Versuch fest. Die [Arbeitsvorlagen](chat-arbeitsvorlagen.md#durchgehender-übungsfall) enthalten einen vollständigen Anwendungsfall.

## Fachliche Prüfung vor der Wiederaufnahme

Leite aus dem Prüfergebnis die [nächste zulässige Aktion](build-control.md#wiederaufnahme-und-sichtbarer-status) für den betroffenen Strang ab und übergib sie an den vorhandenen Fachablauf. Der Checkpoint führt den bestehenden Rückkehranker und den beobachteten Zustand weiter.

Prüfe bei WEITER und NEXT CHAT einen importierten oder seit dem letzten bestätigten Stand geänderten Checkpoint einmal vor der Übergabe an den Fachablauf. Verwende bei einem strukturierten Format zuerst das belegte, zum Format gehörende Schema, soweit verfügbar. Bei fehlendem Schema kennzeichne die formale Abnahme als offen und prüfe die belegbaren Inhalte dennoch. Prüfe Bedeutung und Herkunft anhand des tatsächlichen Projektstands. Halte pro betroffenem Strang Ergebnis, Beleg, offene Voraussetzung und nächsten zulässigen Schritt für Fachablauf und Daemon fest. Verwende bei älteren Text-Handoffs die belegten Felder und kennzeichne fehlende Informationen als offen. Beispiele bleiben Beispiele.

1. Gleiche Projekt, Linie, Basis, Scope und Rückkehranker mit der maßgeblichen Quelle ab. Ein Handoff überträgt Sachstand. Schreibbefugnis folgt dem aktuellen Nutzerauftrag und der nativen Projektgrenze.
2. Prüfe bei Strängen eindeutige IDs, auflösbare Vorgänger und den Abhängigkeitsgraphen auf Selbstbezüge und Zyklen. Prüfe bei Ereignissen Reihenfolge und Inhalt. Eine Korrektur verweist auf das ersetzte Ereignis. Gleiche ID mit abweichendem Inhalt bleibt als Konflikt sichtbar.
3. Prüfe bei gemeldetem Abschluss erwartetes und beobachtetes Ergebnis, Beleg und betroffene Revision, erforderliche Vorgänger, Readback falls nötig und offene Blocker. Eine leere oder sachfremde Evidenzliste trägt keinen verifizierten Abschluss. Ein unbekannter Schreibausgang wird vor Wiederholung anhand des tatsächlichen Ziels abgeglichen.
4. Halte einen Defekt am betroffenen Strang fest. Seine abhängigen Stränge warten, solange der benötigte Vorgänger ungeklärt ist. Unabhängige Arbeit mit geprüfter Basis und gültigem Auftrag bleibt ausführbar. Bei uneindeutiger Projektidentität oder ungeklärter Basis bleibt jede davon abhängige Wiederaufnahme offen.

| Gegenprobe | Erwartung vor der Wiederaufnahme |
| --- | --- |
| Eindeutige Stränge, belegte Vorgänger und passende Revision | Erste offene und zulässige Aktion übernehmen. |
| Doppelte Strang-ID | Betroffene Identität und abhängige Schritte bis zur Klärung zurückhalten. |
| Nicht vorhandener Vorgänger | Abhängigkeit als offen ausweisen. |
| Selbstabhängigkeit oder mehrgliedriger Zyklus | Beteiligte Stränge und davon abhängige Schritte zurückhalten. |
| VERIFIZIERT ohne passende Evidenz | Status offen halten und den fehlenden Nachweis nennen. |
| Geänderte Basis bei weiterhin belegter Projektlinie | Betroffene Nachweise anhand der [Auswirkungsprüfung](../skills/sceeri-repository-intelligence/SKILL.md#gezielte-nachprüfung-nach-quelländerungen) neu prüfen. |

Die vier negativen Importfälle zu doppelter ID, unbekanntem Vorgänger, Selbstabhängigkeit und leerer Evidenz wurden am Schema aus CodeForge-Handoff-UCA-R01 beobachtet. Die Tabelle beschreibt die zusätzlichen fachlichen Prüferwartungen. Ein Lauf im ChatGPT-Host erhält einen eigenen Nachweis.

Übernimm bei mehrstufiger Arbeit die belegten Teilaufgaben mit IDs und ihren Abhängigkeiten nach [Aufgaben, Sammlung und Fortschritt](build-control.md#aufgaben-sammlung-und-fortschritt). Ein Handoff führt aktive Aufgaben, offen gebliebene Prüfungen und die belegte Rückkehrbasis gemeinsam weiter.

## Strukturhilfe für CodeForge-UCA-v1

Die [Wiederaufnahme-Prüfung](wiederaufnahme-pruefung.md) verbindet den Zielabgleich mit der optionalen lesenden Graphprüfung. Führe bei einem Handoff, der einen Host-Lauf oder Write behauptet, zusätzlich eine unabhängige Prüfung des tatsächlichen Ziels durch.

## Git-Rehydration mit Auswirkungsprüfung

```text
python skills/sceeri-coding-profi-livecircle/scripts/checkpoint_review.py checkpoint.json binding.json --git-repo /pfad/zum/projekt
```

Verwende den tatsächlich aufgelösten Projektpfad und eine separat geprüfte aktuelle Bindung mit `project`, `lineage_id`, `scope` und `base_commit`. Beide Commit-Objekte müssen lokal verfügbar sein. Herkunft, Remote-Autorität, lokale uncommittete Änderungen und Schreibfreigaben werden separat geprüft. Der Git-Modus vergleicht ausschließlich die beiden bestätigten Commit-Bäume und lehnt eine rückwärts gerichtete oder divergente Abstammung ab.

Optional beschreibt `contract_paths` pro Strang repo-relative Dateien und Verzeichnisse, die den Befund, das Verhalten und die Abnahme tragen. Dazu gehören je nach Fall Aufrufer, Konfiguration, Lockfiles und Tests. Leite die Liste aus dem semantisch verstandenen Pfad ab. Ein Treffer im Diff ist ein Anlass zur Gegenprobe und kein Ursachennachweis. Gleiche bei geänderten externen Verträgen oder Umgebungen deren Belege separat ab.

| Ergebnis | Aktion im LiveCircle |
| --- | --- |
| `READBACK` | `write_outcome` ist `unknown` oder `readback_pending`. Tatsächliches Ziel lesen, bevor eine erneute Veränderung in Frage kommt. |
| `REVALIDATE` | Ein belegter Vertragspfad hat sich geändert. Wirkung, alternative Ursache und notwendige Laufzeitgegenprobe aktualisieren. Abhängige Schritte warten. |
| `BIND_EVIDENCE` | Neuer Commit ohne gültige Pfadbindung dieses Strangs. Fundstellen und Belege auf der aktuellen Basis zuordnen, dann neu prüfen. |
| `CANDIDATE` | Struktur und betrachtete Pfade erlauben die weitere Prüfung des nächsten Schritts im aktuellen Auftrag. |

`--confirmed-complete STRAND_ID` zählt nur bei unabhängiger, zum aktuellen Vertrag passender Evidenz. Betroffene Stränge verlieren selbst bei diesem Schalter die Wiederaufnahmefreigabe. Nach bestätigtem Gegenbeleg oder Repair wird der Checkpoint anhand des tatsächlichen Ergebnisses auf der neuen Basis aktualisiert und abermals geprüft. Der Checkpoint-Prüfer schreibt weder ins Repository noch in das Zielsystem.

### Lokalen Arbeitsstand mitprüfen

Für eine Fortsetzung in einem bekannten lokalen Checkout ergänze `--include-worktree`. Der Checkout muss auf dem aktuell gebundenen Commit stehen. Der Prüfer erfasst Index, ungestagte Änderungen, ungetrackte sichtbare Dateien und ungelöste Git-Konflikte. Er benutzt die Vereinigung ihrer Pfade mit dem Commit-Diff. Index und Arbeitsbaum können beide betroffen sein, selbst wenn der Arbeitsbaum den alten Dateiinhalt wieder zeigt. Die Herkunft der für den Strang relevanten lokalen Pfade erscheint unter `worktree.relevant_paths`.

Bei `RESOLVE_CONFLICT` kläre die betroffenen lokalen Inhalte und ihre Herkunft über das zuständige Git-Verfahren. Bei unklarem Schreibausgang bleibt Ziel-Readback vorrangig. Bei verändertem HEAD prüfe die lokale Git-Projektbindung unabhängig neu. Unabhängige Stränge bleiben bei belegter Basis und unberührten Vertragspfaden fortsetzbar.

Der Abgleich ist eine lesende Momentaufnahme des Git-Status. Ignorierte Dateien und externe Ressourcen folgen dem jeweiligen Projekt-Nachweis. Prüfe vor einem Schreibschritt die Basis erneut, falls der Arbeitsbaum zwischenzeitlich geändert werden konnte. Der bisherige Commit-only-Modus bleibt für Remote-Bindungen oder einen lokal verfügbaren Commit ohne passenden Checkout verfügbar.
