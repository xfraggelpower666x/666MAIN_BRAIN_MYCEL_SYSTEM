# Controlled Learning Policy v1.5.0

## Lernobjekt

Eine Korrektur erzeugt ausschließlich einen `Correction Learning Candidate`.

## Promotion

```text
SESSION_ONLY
→ PROJECT_CANDIDATE
→ HUMAN_CONFIRMED
→ CANONICAL_PENDING
```

Jeder Schritt benötigt eine explizite, belegbare Entscheidung. Überspringen ist unzulässig.

## Konflikte

Zwei Kandidaten mit demselben Ausgangskontext, aber widersprüchlichen Zielkorrekturen werden nicht
zusammengeführt. Beide wechseln in `CONFLICT_QUARANTINE`.

## Datenschutz

Standardmäßig werden nur SHA-256-Hashes, Fehlerklassen und abstrahierte Merkmale gespeichert.
Private Rohtexte werden nur bei ausdrücklich freigegebenen Testfixtures aufgenommen.

## Aktivierung

Ein Kandidat darf frühestens nach dem vollständigen nächsten Stufenzyklus kanonisch werden.
