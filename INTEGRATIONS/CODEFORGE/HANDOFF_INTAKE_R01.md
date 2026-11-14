# CodeForge → Universal Code Agent · Handoff Intake R01

Status: Dokumentation und Eingabebelege aufgenommen
Stand: 2026-11-14
MAIN-BRAIN-Basis: `00d744f33145d119f666cc5c42fe9fc3287edfb3`
Ziel: Wiederverwendbare Entwicklungsverträge für einen späteren UCA-Einbau

## Herkunft und Reichweite

Die Prüfsummen binden die fünf lokal vorliegenden Eingaben. Referenzcommits sind Angaben der Handoffs. Sie sind keine Live-Pointer.

| Eingabe | SHA-256 | Beitrag |
|---|---|---|
| CodeForge-Handoff-UCA-R01 | `bd5001a680e9ac76de2666b0aed1fe244e5e31a0936a89f357a5144da4724e71` | Agentenauftrag, versionierter Checkpoint, Strang- und Unterbrechungsvertrag |
| 666PFS CodeForge R01 | `19259469c725e2d085b80bf295e621a401c6005692128afe98236447f5839bcc` | Preimage, Allowlist, Backup, isoliertes Apply, Journal und Rollback |
| 666STREAM Radio-CodeForge v1.0.0 | `87355055a957030f5d5bb16444827a2ff107224a8af68de7b1d0a14f9fb67487` | Entwicklungsvertrag und unabhängige Prüfung von Code, Tests und Artefakten |
| 666STREAM Multiprojekt-Bauanleitung v1.0.0 | `29ca46314215f55f5220debbd4a492b63c3b3e1031bd033f9b5e34b4dcbc2f3f` | Projekt-IDs, Aliasauflösung, Scope pro Chat und commitgebundener Current |
| Claude Code in VS Code, Dokumentationsauszug | `7315dee23c20b5d6342a2f90964af4c9350e46c4c81b8e95a0be947071cf6d6f` | Optionale Host-Anbindung für Editor-Kontext, Sitzungsfortsetzung und MCP |

Lokal geprüft wurden ZIP-Integrität und das Checkpoint-Beispiel gegen das mitgelieferte JSON-Schema. Die Uploads bleiben an ihrer Herkunft. Dieser Intake übernimmt abstrahierte Verträge als Peer-Evidenz. Die [RepoBrain-R01-Schnittstelle](../REPOBRAIN/README.md) ist ein möglicher Graph-Zulieferer mit eigener Evidenzgrenze.

## Integrationsvertrag für den Zielagenten

1. **Projekt auflösen.** Der Router akzeptiert direkte Nutzertrigger. Die Ziel-Registry liefert Projekt-ID und erlaubten Scope. Bei mehrdeutigem Alias erst das Ziel klären. Je Sitzung das Projekt gesondert binden. Repository-HEAD, Struktur-Body, Projekt-Commit und Deployment jeweils separat ausweisen.
2. **Basis und Rückkehranker prüfen.** Projekt-Ref auf Commit fixieren, Manifest und erforderliche Quellen lesen. Checkpoint an Projekt, Commit, Scope und Lineage binden. Nach HEAD-Wechsel die betroffenen Pfade und Belege erneut bewerten.
3. **Reparatur isolieren.** Symptom am normalen Einstieg belegen. Patch auf die erlaubten Pfade begrenzen. Preimage, Diff, Backup und Rollback-Ziel festhalten. Ausführung und Veröffentlichung folgen der Authority des Zielprojekts.
4. **Wirkung belegen.** Statische Graphkanten und beobachtete API-, Event- oder Bridge-Laufzeit getrennt ausweisen. Unabhängige Tests gegen den Kandidaten ausführen und Ergebnisse mit Befehl, Umgebung und Basis verankern. RepoBrain-Daten bleiben Evidenz. Commit-Metadaten des Graphen erfordern einen eigenen Herkunftsnachweis.
5. **Stränge fortsetzen.** Unabhängige Arbeit nach Dateibesitz und Abhängigkeiten koordinieren. Gemeinsame Ziele serialisieren. Checkpoints halten erledigte Arbeit, offenen Blocker, nächste Aktion und verifizierbare Belege je Strang fest.
6. **Host abnehmen.** Im echten Zielhost Aliasmehrdeutigkeit, Isolation zweier Chats, Wiederaufnahme nach Unterbrechung und geänderten HEAD prüfen. Editor und MCP sind optionale Provider mit den Rechten des Zielprojekts.

## Statusgrenzen

| Ebene | Befund |
|---|---|
| Quelle | Fünf lokale Eingaben erfasst. ZIP und Checkpoint-Beispiel lokal geprüft. |
| Skill-Discovery | Der Intake erhebt keine neue Discovery-Evidenz. Maßgeblich bleibt die bestehende MAIN-BRAIN-Hostmatrix. |
| Routing | Integrationsvertrag dokumentiert. Zielagentenlauf offen. |
| Host-Verhalten | UCA-Checkout, UCA-Host-Bindung und Fresh-Chat-Abnahme offen. |

Der Intake ändert keine native Runtime. Die sechs MAIN-BRAIN-Stränge, die Migrationsautorität und die vorhandene [Fresh-Chat-Matrix](../../HOST/FRESH_CHAT_ACCEPTANCE_MATRIX.md) bleiben eigenständig maßgeblich.
