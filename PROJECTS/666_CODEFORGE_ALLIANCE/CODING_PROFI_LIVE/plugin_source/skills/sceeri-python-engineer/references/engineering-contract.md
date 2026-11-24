# Engineering contract

- Quality: correct behavior, stable public interfaces, type/exception discipline, deterministic tests, documented failure cases, clear causal diagnosis.
- Security review: untrusted input, serialization, shell execution, file traversal, URL fetches, dynamic imports, dangerous eval, secret leakage, dependency trust.
- Severity: CRITICAL / HIGH / MEDIUM / LOW / INFORMATIONAL. Findings from pattern detection are hypotheses; require line-level confirmation.
- Build gates: Python syntax, unit tests, regression tests, changed-file hashing, expected behaviors, independent readback, complete file inventory.
- Code review: avoid vague 'fixed' claims. For each change include evidence ID, before/after expected behavior, test command, actual result and rollback path.
- Multisystem scope: plugin skill can be reused by independent systems, but never claims authority over their code, pointers, names, trademarks, branches or policies.
