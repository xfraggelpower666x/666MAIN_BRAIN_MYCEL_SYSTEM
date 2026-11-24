---
name: sceeri-evidence
description: Verify assertions through source provenance, direct readback, recency and contradiction control.
---

# sceeri-evidence

1. Require immutable source identifiers for factual claims when available; classify user statement, repository evidence, observed execution, test report, tool output and inference.
2. Compare source authority and recency; a current verified native pointer outranks stale history, but never silently promote backups.
3. Mark SEARCH_RESULT != READBACK, FOUND != VERIFIED, TEST_PASS != HOST_ACCEPTANCE.
4. Record source timestamp, scope, content fingerprint when available, verification method, limitations, and negative findings.
5. Never invent receipts, HEADs, test outcomes, external access or completed actions. Missing evidence remains OFFEN or BLOCKIERT.
6. Apply freshness checks before decisions depending on current state.

## Technische Entscheidung mit Gegenbeleg

Bei mehreren plausiblen Erklärungen dokumentiere je Hypothese Beobachtung, genaue Quelle, Unsicherheit, Entscheidung und eine Beobachtung, die sie widerlegen würde. Wähle den Beleg passend zur Aussage. Eine reproduzierbare Gegenprobe stützt Verhalten, die Quellstelle den Mechanismus, eine Messreihe eine Leistungsbehauptung und ein Vertrag das Soll. Führe bei widersprüchlichen Belegen Quelle, Revision und Prüfbedingungen getrennt. Verwende keine aus Beispielwerten abgeleiteten numerischen Konfidenzen.
