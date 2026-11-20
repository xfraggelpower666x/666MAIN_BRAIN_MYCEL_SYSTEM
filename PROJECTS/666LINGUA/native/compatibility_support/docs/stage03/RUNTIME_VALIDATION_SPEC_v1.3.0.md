# STAGE 03 — Runtime Validation Specification v1.3.0

**SYSTEM_ID:** `LYVRA-DOLMETSCHER-001`  
**Status:** `LOCAL_RUNTIME_EXECUTION`  
**Baseline:** `v1.2.4`  
**Stage-02-Status:** `INTERRUPTED_OPEN`

## Ziel

Die im Chat-Backup entwickelten Anforderungen werden nicht nur dokumentiert, sondern über einen
reproduzierbaren lokalen Referenz-Validator ausgeführt. Der Validator prüft Zustandsübergänge, Routing,
Korrekturbeziehungen, Diktierentscheidungen, Ausgabeintegrität, HOLD, Confidence, Companion-Isolation,
Schemas und externe Systemgrenzen.

## Validierungsebenen

1. `STRUCTURAL_RUNTIME_VALIDATION`
2. `STATE_AND_ROUTING_SIMULATION`
3. `OUTPUT_INTEGRITY_FIXTURES`
4. `LINGUISTIC_MODEL_RUNTIME_VALIDATION`

Nur die ersten drei Ebenen sind im Paket lokal ausführbar. Ebene 4 benötigt einen tatsächlichen
mehrsprachigen Modell-/Host-Lauf.

## Definition of Local Pass

- alle lokalen Runtime-Fälle PASS;
- beide JSON-Schemas validierbar;
- Baseline-Testdefinitionen unverändert vorhanden;
- kein Drive-, Registry-, Pointer-, PFS-Core- oder LYVRA-Write;
- keine Behauptung eines ausgeführten Modell-Sprachtests.

## Ausführung

```text
python tools/runtime_validation.py <PROJECT_ROOT>
```
