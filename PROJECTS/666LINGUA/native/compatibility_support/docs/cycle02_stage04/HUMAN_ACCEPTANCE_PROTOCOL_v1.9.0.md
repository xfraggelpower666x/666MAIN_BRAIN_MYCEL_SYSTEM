# Human Acceptance Protocol v1.9.0

## Ziel
Unabhängige zweisprachige Prüfer bewerten Bedeutung, natürliche Zielsprachlichkeit, Beziehung, Mehrfach-Emotionen, Humor, Ironie, Diktierkorrektur, Emoji-Verstärkung und Format-Erhalt.

## Verfahren
Jeder Fall wird blind gegen Ausgangstext und Zielprofil geprüft. Zulässig sind PASS, FAIL oder CONFLICT_QUARANTINE. Ein FAIL darf nicht durch Mehrheitsentscheidung verdeckt werden. Gleichrangige widersprüchliche Bewertungen werden quarantänisiert.

## Pflichtfelder
case_id, source_language, target_profile, source_text_hash, reviewer_role, semantic_fidelity, naturalness, emotional_fidelity, relationship_fidelity, emoji_integrity, formatting_integrity, verdict, evidence_note.

## Externe Grenze
Eine echte unabhängige zweisprachige Prüfung wurde in diesem Host nicht durchgeführt und bleibt PENDING_EXTERNAL.
