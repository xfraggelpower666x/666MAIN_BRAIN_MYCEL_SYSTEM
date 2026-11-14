# CodeForge R09 · SunoCleanser Repair

Basis: `13671e5cfd54f9fd0974d9b17cc48765d985b99e`  
Getesteter lokaler Kandidat: `f9d644ebd4b5f6c4b757d06febd672e48f9f3d23`  
Getesteter Projekt-Tree: `c3d936b6ec20bbd0e60fd744bcb71e6c925fe4ae`

- Importreihenfolge und bestätigte Lint-Befunde korrigiert. Die Ausnahmegrenzen der CLI und GUI bleiben mit begründeten lokalen Ruff-Ausnahmen erhalten.
- SciPy-Fensteraufrufe behalten ihre bisherigen ndarray-Parameter. Pyright-Ausnahmen sind auf die beiden unvollständig typisierten Parameter beschränkt. Der Rückgabetyp des Nulltests bildet numerische Felder und die dBFS-Referenz getrennt ab. Ein Eingang ohne Audiokanäle wird vor der Spektralverarbeitung abgefangen.
- Changelog und Projektprüfsummen aktualisiert. Die Prüfsummenliste wurde vollständig geprüft.

| Prüfung | Ergebnis |
|---|---|
| PyGate 0.3.2 Full | PASS |
| Ruff 0.17.5 | PASS |
| Pyright 1.1.414 | PASS |
| pytest 9.2.0 | 24/24 PASS |
| CodeForge R07 | REVIEW_EVIDENCE_CONSISTENT, 11/11 Patch-Pfade im Beleg, 0 außerhalb des Projektscopes |

Laufumgebung: Linux x86_64, Python 3.12.14. Der Lauf verwendete eine isolierte lokale Umgebung mit den verfügbaren Projektabhängigkeiten, keine neue Abnahme der Frozen-Lock-Umgebung. Windows-GUI sowie Fresh-Chat- und UCA-Host bleiben offen.

Snapshot: `ac23e42e94da8d3f3677d7069f75a2dfcfa2017c6568dc81bb70dc95d7de709c`  
SHA-256 lokaler PyGate-Beleg: `d8fb177de610d3c9537505e8921220798eb9267531e146f4bfe53f4f35a2a8ce`
