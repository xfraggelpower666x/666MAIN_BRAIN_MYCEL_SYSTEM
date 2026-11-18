# Human Review Authority Model v1.7.0

## Evidenzstufen

```text
L0_CURRENT_HOST_SELF_REVIEW
L1_USER_CORRECTION
L2_BILINGUAL_HUMAN_REVIEW
L3_AUTHORIZED_DOMAIN_REVIEW
L4_MULTI_REVIEWER_CONSENSUS
```

## Rechte

| Stufe | Darf Fehler markieren | Darf Kandidat erzeugen | Darf Scope erhöhen | Darf kanonisch aktivieren |
|---|---:|---:|---:|---:|
| L0 | ja | ja | nein | nein |
| L1 | ja | ja | bis PROJECT_CANDIDATE | nein |
| L2 | ja | ja | bis HUMAN_CONFIRMED | nein |
| L3 | ja | ja | bis HUMAN_CONFIRMED | nein |
| L4 | ja | ja | CANONICAL_PENDING vorschlagen | nein |

Kanonische Aktivierung erfolgt niemals durch Review allein. Sie benötigt den vollständigen Stufenzyklus,
Audit, Regression und Freeze.

## Konflikte

Widersprüchliche Reviews erhalten getrennte Evidenzobjekte und wechseln in `CONFLICT_QUARANTINE`.
Mehrheitsentscheidung allein reicht nicht; Kontext, Profil und Reviewer-Scope müssen berücksichtigt werden.
