# CONTINUITY AND HANDOFF CONTRACT

CONTINUITY_OWNER=666MAIN BRAIN MYCEL SYSTEM
HANDOFF_FORMAT=EVIDENCE_FIRST

## Handoff minimum

- SOURCE_SYSTEM
- TARGET_SYSTEM
- PURPOSE
- VERIFIED_CURRENT_POINTER_REFERENCE
- VERIFIED_STATE_REFERENCE
- OPEN_WORK
- COMPLETED_WORK
- BLOCKERS
- RETURN_ANCHOR
- PROVENANCE
- SUPERSESSION
- CONSUMPTION_STATUS

## Rules

HANDOFF_NE_AUTHORITY=TRUE
HANDOFF_NE_CURRENT_POINTER=TRUE
UNCONSUMED_HANDOFF_MAY_BE_DELTA_INPUT=TRUE
STALE_HANDOFF_MUST_REVALIDATE=TRUE
TARGET_NATIVE_SYSTEM_INTERPRETS_HANDOFF=TRUE
MAIN_BRAIN_MAY_CATALOG_HANDOFF_RELATION=TRUE
MAIN_BRAIN_MAY_NOT_EXECUTE_FOREIGN_WRITE_BY_HANDOFF_ALONE=TRUE

## CodeForge-Checkpoint

Je Arbeitsstrang Repository-ID, Branch, Basis- und Kandidatencommit, Pfad-Scope, abhängige Verträge, letzte verifizierte Aktion, offene Verpflichtungen und Return-Anchor festhalten. Prüfbelege an Objekt-IDs und Ausführungsumgebung binden. Verwende bei einer beobachteten Run-Adoption eine stabile Ereignis-ID mit Repository-ID, Kandidatencommit, Provider, Run-ID und Artefakt-ID.

Wenn der Lauf abgeschlossen ist und die Arbeitsposition hinterherhinkt, Run und Receipt direkt lesen. Bei derselben Ereignis-ID den vorhandenen Eintrag verwenden. Nach verändertem HEAD nur betroffene Belege anhand ihrer Eingaben, Pfade und Umgebung neu bewerten. Gemeinsame Ledger-Schreibvorgänge folgen der nativen Lock- und Queue-Governance.

Bei Peer-Handoffs referenziert jeder Beleg Handoff-ID und Quellrevision. Zustellung, Readback, Adoption und Host-Ausführung werden einzeln belegt. Die Zielinstanz entscheidet über die Übernahme.

### Methodenwechsel nach Unterbrechung

Speichere bei fehlgeschlagenen Wiederholungen die Task-ID, Fehlersignatur, Quellfingerprint, Methode und Zahl der Versuche im vorhandenen Strang-Checkpoint. Nach höchstens drei identischen Versuchen einen begründeten Methodenwechsel oder den konkreten Blocker erfassen. Bei eindeutigem Rechte- oder Authority-Blocker sofort den betroffenen Strang pausieren. Unabhängige Stränge behalten ihre belegte Arbeitsposition.
