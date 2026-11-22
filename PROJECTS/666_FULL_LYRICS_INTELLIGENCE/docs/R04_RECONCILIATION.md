# R04 Read-only Project Reconciliation

A local analyzer compares only indexed catalog categories and source counts against a user-supplied Current candidate. It never modifies any foreign repository or invokes native system triggers.

Usage (from the project's own Windows PC Python environment):

```powershell
python engine/reconciliation.py --catalog "<local catalog-data>\catalog.sqlite" --project LYVRA --native-current "<verified downloaded Current>.json" --expected-sha256 "<sha256>" --output "<local report>.json"
```

The SHA-256 check verifies equality with the *supplied fingerprint*, **not** GitHub authority or a native Current pointer. The result remains `REVIEW_REQUIRED`; the actual native authority must be independently verified before any integration decision. No automatic writes are performed. The source file and generated report remain local, not in the public repo.

Four new negative and positive tests cover missing current, catalog counts, hash match without native authority, and conflicting hash.
