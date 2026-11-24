# Prompt specification

Each prompt must have: PROJECT / SOURCE EVIDENCE / OBJECTIVE / IN-SCOPE / OUT-OF-SCOPE / BEHAVIOR / TESTS / AUTHORITIES / DELIVERY. State `FOUND != VERIFIED` and `SEARCH_RESULT != READBACK`. Label findings VERIFIZIERT | ABGELEITET | VORGESCHLAGEN | OFFEN | BLOCKIERT. For bug fixes demand reproducer + expected and actual; for refactors behavior parity; for tests no product code modifications unless approved. Explicitly forbid credential exposure and destructive cleanup. Never use aspirational 'automatically self-heal' as a guarantee.

All generated rules respect the repository's existing upstream instructions unless they conflict with authenticated owner directives or security policy. Unknown owner identity is not guessed. Confirm that the code is owned before replacing product branding; preserve upstream legal and license notices.
