# CodeForge R08 · SunoCleanser-Integration

Datum: 2026-11-14  
Scope: `PROJECTS/SunoCleanser-0.2.1`  
GitHub-Checkout des Laufs: `3dbb164d02d388a8c30e8aac208a48dee2e7cc25`  
Import-Kandidat: `e6b79322af07ed9898b453d94c9822a3ee59ab18`  
Basis des Import-Diffs: `cbf7d7c1acd885a80a8f5a9254a165eefb145879`  
Projekt-Tree beim Lauf und beim Import: `d078421ead3d5d599ac989d3c343d771e095ee82`

## Beobachtung

Der Lauf verwendete den Originalcheckout auf Linux x86_64 mit Python 3.12.14. Git-Diff und Projekt-Tree bestätigten, dass sich der Projektbereich seit dem Import nicht verändert hatte. Der Arbeitsbaum war nach Entfernung der temporären Runner-Konfiguration sauber. Der Import-Diff lieferte die Liste der 36 geprüften Pfade. Das Ergebnis war weder abgeschnitten noch meldete der Runner eine Snapshot-Änderung.

| Prüfer | Ergebnis | Befund |
|---|---|---|
| Ruff 0.17.5 | FAIL, Exit 1 | 11 Befunde, unter anderem Importsortierung und breite Exception-Handler. |
| Pyright 1.1.414 | FAIL, Exit 1 | 6 Befunde, unter anderem SciPy-Typen, Rückgabetypen und optionale Frequenzdaten. |
| pytest 9.2.0 | PASS, Exit 0 | 24 von 24 vorhandenen Tests bestanden. |
| PyGate 0.3.2 | FAIL, Exit 1 | 17 Befunde über Lint und Typprüfung. |
| CodeForge R07 auf dem Import-Kandidaten | QUALITY_EVIDENCE_INCOMPLETE, Exit 1 | Snapshot aus regulären Git-Blobs stimmt, 36 geänderte Pfade, 0 außerhalb des Scopes, 0 im Beleg fehlend. |
| CodeForge R07 mit Branch-HEAD als Kandidat | OUTSIDE_SCOPE, Exit 1 | 33 zusätzliche Pfade liegen außerhalb des erlaubten Projektpfads. |

Beim ersten Versuch aus dem Monorepo-Root konnte pytest das Projektpaket nicht importieren. Der ausgewertete Lauf setzte den Projektpfad in `PYTHONPATH`. Die Projekttests hatten auch beim direkten Aufruf aus dem Projektordner bestanden.

## Reproduktion und Belege

Aus dem Repository-Root die 36 Projektpfade des Import-Diffs mit `git diff --no-renames --name-only BASIS IMPORT -- PROJECTS/SunoCleanser-0.2.1` in eine temporäre Datei schreiben. PyGate im Modus `full` mit `--changed-files` starten. Die lokale Runner-Konfiguration richtet Ruff und Pyright auf den Projektpfad und pytest auf dessen Unterordner `tests`. Für Pyright die Python-Umgebung mit den Projektabhängigkeiten auswählen. Für pytest den Projektpfad in `PYTHONPATH` setzen und das JSON-Report-Plugin aktivieren.

Den [CodeForge-Aufruf](../INTEGRATIONS/CODEFORGE/HANDOFF_INTAKE_R01.md#patch-pfadabdeckung-r07) mit Import-Basis, Import-Kandidat, Projektpfad als Allowlist, `--snapshot-from-candidate`, `--require-patch-coverage` sowie den Pflichtchecks `lint`, `typecheck` und `test` ausführen.

| Beleg | SHA-256 |
|---|---|
| PyGate-Snapshot-Digest | `7e6fc7deb06cd1829fff3b6336e1b2c9cd3a38754e9d82a14d3534432456c160` |
| Lokaler PyGate-Rohbeleg | `30d7e5f63f9bd8864d749b099760ee71781b4d699ed662af75808a7792b5ec21` |
| Lokale CodeForge-Ausgabe zum Import | `d69f508583531427748fe2cf7f75d13e9039a45c4c7a81173c85aac1be13774d` |

Dies ist ein beobachteter lokaler Qualitätslauf. Der Audit veröffentlicht seine Zusammenfassung. Rohlogs und temporäre Konfiguration wurden nicht ins Repository übernommen. Die GitHub-Actions-Abfrage für den Branch lieferte keine Runs, die Suche nach dem UCA-Zielrepository keinen Treffer. Fresh-Chat- und UCA-Host-Abnahme bleiben offen.

Der Branch änderte sich vor der Veröffentlichung durch die Entfernung von Light Wave Tech. Der Checkout des Laufs bleibt oben fixiert. Die geprüfte SunoCleanser-Tree-ID, CodeForge-Einstiege und der Current Pointer blieben beim Wechsel der Publikationsbasis identisch.
