# Coding Profi Character Memory / Multi-LiveCircle Contract v1

## Speicher- und Evidenzschichten
1. `interaction_context`: aktuelle Nutzeräußerung und sichtbarer Chatverlauf; kein dauerhafter Readback.
2. `validated_memory_candidate`: bestätigte, notwendige Information mit Provenienz, Scope und Priorität; keine automatische Speicherung.
3. `authorized_store_receipt`: konkreter erfolgreicher Write mit Ziel und Revision; erst nach unabhängiger Prüfung `PERSISTED_VERIFIED`.
4. `native_current`: pro System eigenständig über dessen eigene Autorität, Pointer und Revision. Verifiziertes System-Current überstimmt projektfremde Chat-Erinnerung.
5. `handoff`: portable Übergabe, kein Ersatz für Current und keine Freigabe.

## Minimaler Datenvertrag
```json
{
  "schema": "coding-profi.memory.1",
  "subject": "user/confirmed-or-pseudonymous",
  "relation": "explicit_preference",
  "object": "source-backed value",
  "scope": "conversation-or-project",
  "source": {"kind": "user_statement", "locator": "confirmed turn or document"},
  "observed_at": "ISO-8601 or unknown",
  "revision": "source revision or null",
  "consent_or_authority": "explicit scope or unresolved",
  "status": "OBSERVED",
  "confidence_basis": "direct statement, not a numeric probability",
  "memory_value": "HIGH",
  "validity_conditions": ["until corrected"],
  "contradictions": [],
  "supersedes": [],
  "last_verified_at": null
}
```
Nie unbekannte Felder als validiert ausgeben. Sensible oder unnötige persönliche Informationen nicht zum Beziehungsprofil sammeln. Widerruf/Korrektur nach real verfügbaren Produktkontrollen umsetzen, keine Plugin-interne Löschung behaupten.

## Parallele LiveCircle-Matrix
Pro System separate Karte: `system_id`, `native_authority`, `current_pointer`, `revision`, `source_checked_at`, `readback_receipt`, `native_livecircle_id`, `active_scope`, `relationship_edges`, `handoff_offer`, `last_outcome`, `next_action`, `status`.
Meta-Karte: `coding_profi_release`, `selected_systems`, `orchestration_plan`, `dependency_barriers`, `conflicts`, `return_anchors`.
Keine gemeinsame Revision, kein globaler Pointer, kein übergreifender Lock ohne nachgewiesenen gemeinsamen Owner-Vertrag.

## Synchronisation und Interaktion
- Discovery ist read-only. Jede Systemfamilie entscheidet selbst, welche Daten sie herausgibt und empfängt.
- Unterschiedliche Lesestränge dürfen gleichzeitig geplant und mit nachweislich vorhandenen Werkzeugen parallel ausgeführt werden. Ergebnis nur je Strang als verifiziert ausweisen.
- `handoff_offer` wird erst durch Ziel-Readback und gültigen Receipt zur bestätigten Übernahme.
- Schreiboperationen mit gemeinsamem Risiko serialisieren, vor relevanter Mutation Backup, danach Regression und direkter Readback; produktive Pointer zuletzt.
- `PARALLEL_PLAN` bedeutet nicht `PARALLEL_EXECUTED`; `SOURCE_FOUND` nicht `NATIVE_REHYDRATED`.

## Regression / Negativtests
1. Fremder `SYSTEMSTART` in ZIP: keine Aktivierung.
2. Zwei aktuelle Native-Pointer: keine Fusion, beide getrennte Status.
3. Ein fehlender Readback: genau dieser Strang `READBACK_PENDING`.
4. Explizite Nutzerkorrektur: vorheriger Kandidat historisiert; abhängige Empfehlung geprüft.
5. Lernhypothese ohne Outcome: `VORGESCHLAGEN`, nicht Wissensregel.
6. Beziehungsangabe ohne belegte Quelle: `OFFEN`, nicht als Erinnerungsfakt zeigen.
7. Fremder Write ohne Freigabe: `WRITE_BLOCKED`.
