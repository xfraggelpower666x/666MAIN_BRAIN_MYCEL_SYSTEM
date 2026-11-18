# Data Retention and Deletion Model v1.7.0

## Retention classes

```text
TRANSIENT_PROCESSING
SESSION_ONLY
EXPLICIT_TEST_FIXTURE
EXPLICIT_EXPORT
PROHIBITED
```

### TRANSIENT_PROCESSING

- vollständiger aktueller Eingangstext während der Verarbeitung
- temporäre Rekonstruktionskandidaten
- nicht persistente Reverse-Audit-Zwischenergebnisse

Löschung: unmittelbar nach Abschluss oder Abbruch des Verarbeitungsvorgangs.

### SESSION_ONLY

- gehashte semantische Anker
- Korrekturlinie
- Nachrichtenbeziehung
- Lernkandidaten im Status `PROPOSED`

Löschung: bei Session-Ende oder explizitem Forget-Befehl.

### EXPLICIT_TEST_FIXTURE

Private Rohtexte dürfen nur mit ausdrücklicher Freigabe als Testfixture gespeichert werden. Die Freigabe
muss Scope, Zweck und Löschbedingung enthalten.

### EXPLICIT_EXPORT

Exportierte Daten dürfen nur die ausdrücklich gewählten Objekte enthalten. Abgeleitete interne Daten werden
nicht automatisch mitexportiert.

### PROHIBITED

- Secrets
- Zugangsdaten
- Tokens
- Passwörter
- externe Kontaktkennungen ohne zwingenden Zweck
- vollständige private Chatarchive als Standard

## Delete-and-Forget-Graph

Eine Löschung muss mindestens erfassen:

1. Ledger-Einträge
2. Lernkandidaten
3. Human-Review-Evidenz
4. Regressionstest-Kandidaten
5. exportierte lokale Kopien, soweit kontrollierbar
6. Indizes und aktive Pointer
7. Cache- und Checkpoint-Verweise

Hashes gelten als abgeleitete Daten und sind ebenfalls zu löschen, wenn sie auf das zu vergessende Objekt
zurückgeführt werden können.
