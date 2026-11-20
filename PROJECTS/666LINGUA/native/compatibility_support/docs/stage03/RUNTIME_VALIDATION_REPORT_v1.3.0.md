# STAGE 03 — Runtime Validation Report v1.3.0

## Ergebnis

```text
LOCAL_CASES=48
LOCAL_PASSED=48
LOCAL_FAILED=0
LOCAL_STATUS=PASS
OVERALL_STATUS=PARTIAL_PASS
LINGUISTIC_MODEL_RUNTIME=NOT_PERFORMED
```

## Erster Lauf

- 46 von 48 lokalen Fällen PASS
- `RT-REL-001`: Präzisierung fälschlich als Extension klassifiziert
- `RT-DICT-001`: Schlusspunkt nach Deduplizierung verloren

## Minimalinvasive Reparatur

- Kontrastpräzisierungen wie „ein bisschen“ → „ganz“ werden bei gemeinsamem Gegenstand als Korrektur erkannt.
- Die Diktier-Deduplizierung erhält das originale Satzschlusszeichen.

## Re-Audit

- 48 von 48 lokalen Fällen PASS
- 0 lokale Fehler
- 1 externer Sprachmodellbereich bewusst `NOT_PERFORMED`

## Aussagegrenze

`PARTIAL_PASS` bedeutet: Die ausführbare lokale Vertragsruntime ist bestanden. Es bedeutet **nicht**,
dass echte Übersetzungen in allen sechs Sprachprofilen bereits durch ein Modell erzeugt und menschlich
abgenommen wurden.
