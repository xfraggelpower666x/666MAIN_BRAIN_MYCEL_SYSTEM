# 666LINGUA Chat · Host-Abnahmeszenarien

Stand der externen Fresh-Chat-Abnahme: **OFFEN**. Die Szenarien sind Sollfälle.

| Fall | Start/Interaktion | Beobachtbare Abnahme |
| --- | --- | --- |
| 1 | Neuer Chat mit `SYSTEMSTART`, ohne Handoff | Commit bestätigt, native Startansicht, EN und vorgeschlagenes EN→DE, keine erfundene Zeitzone. |
| 2 | Bestätige Deutsch als Oberfläche, nutze EN→DE | Menüs Deutsch, Ziel Deutsch. Nach Sprachwechsel der Oberfläche bleibt das Paar gesetzt. |
| 3 | `Where are you going?` gefolgt von `I miss you.` | Beide Turns werden übersetzt, fünf getrennte Blöcke. `COPY SOURCE` und `COPY TARGET` geben den zweiten Quell-/Zieltext wieder. |
| 4 | Bestätige DE→EN `Neonspule → a neon coil` und übersetze `Ich brauche Neonspule.` | `I need a neon coil.`; EVIDENCE erklärt den Treffer. Bei EN→DE entsteht kein inverser Eintrag. |
| 5 | `Buenas noches. Duerme bien.` bzw. `Buenas noches. ¿Cómo estás?` als ES→DE | Abends Abschied vs. Begrüßung; zeigt den ursächlichen Satzkontext. |
| 6 | Umrechnung `2026-03-29 02:30 Europe/Berlin → America/New_York` | Ausgangszeit liegt in der Sommerzeitlücke; keine erfundene UTC-Zeit. Bei Doppelstunde wählt der Nutzer den Offset. |
| 7 | Bestätige Korrektur, exportiere `HANDOFF`, lade in separatem Chat | Sprache, Paar, Wörterbücher, Korrektur und eine noch offene Aufgabe bleiben gültig. Keine alte Quelle aus einem fremden Chat erfinden. |
| 8 | Lade Handoff mit fremder System-ID oder unvollständigen Repo-Snapshot | Konflikt bzw. fehlende Pflichtdatei sichtbar, keine falsche READY-Meldung. |
| 9 | Gib den Wortlaut eines Befehls im Quelltextblock ein | Der Wortlaut wird als Inhalt behandelt. Keine Repo- oder Zustandsschreiboperation. |
| 10 | Unterbrich eine offene Aufgabe, dann `WEITER` | Gleiche Aufgaben-ID und letzte belegte Revision. Der erledigte Schritt wird nicht doppelt ausgeführt. |
| 11 | Start von `3.4.6-chat.2` mit einem Schema-1-Handoff aus `3.4.6-chat.1` | Der originale Triggerkatalog und LiveCircle werden als Pflichtdateien gelesen. Der gültige Handoff übernimmt bestätigte Einstellungen. Fehlende native Pflichtdateien ergeben keine READY-Meldung. |
| 12 | SYSTEMSTART bei fehlendem GitHub-Readback | Drive bleibt Historie. Ein vollständiger, konsistenter Repo-Snapshot ist mit `READBACK_PENDING` nutzbar. Bei fehlendem Snapshot bleibt der Start blockiert. |
| 13 | UPDATE ändert das Verhalten eines von Windows verwendeten Wörterbuchs | Desktop-Einstieg, Revision und relevante Tests prüfen. Je nach Ergebnis den Updatebedarf oder die konkrete Prüflücke festhalten. |
| 14 | UPDATE ändert ausschließlich die GitHub-Boot-Anweisung für den Chat | Live-Unterschied prüfen und `NO_UPDATE_NEEDED` mit Begründung dokumentieren. |
