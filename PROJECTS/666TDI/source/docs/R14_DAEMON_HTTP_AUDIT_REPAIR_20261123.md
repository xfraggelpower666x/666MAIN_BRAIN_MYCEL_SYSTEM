# 666TDI R1.4 – Daemon Audit & Minimal Repair (2026-11-23)

## Source and authority
- TDI native owner: `666TDI-001`, repo `xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM`, productive branch `666MAIN_BRAIN`, scope `PROJECTS/666TDI/`.
- Baseline audit HEAD: `5b1db9590f8c33051f6371e591729c07b0054c5f`.
- Preserve R0.9 semantic intelligence, R1.0 creative causal reasoning, R1.1 daemon UI, R1.2 chapter preanalysis, R1.3 device translations, and R1.4 creator feedback.
- Coder's review-and-improve skill and Coding L.Y.V.R.A.'s engineering/review skills were read as advisory methods; no external builder, plugin deployment, foreign activation, or cross-system authority used.

## Findings and repair
1. HIGH / local request origin integrity: `source/engine/daemon_cli.py` verified that `_safe_origin` checked the optional Origin header but did not validate `Host`. The server listens on `127.0.0.1`, yet this alone cannot enforce allowed HTTP hostnames. Repair: explicit one-Host localhost/127.0.0.1 plus exact-port gate for **every GET and POST**, before rendering HTML or accepting feedback. Malformed / duplicate / foreign host values return 403 `HOST_NOT_ALLOWED`. Origin parsing is also guarded against invalid ports and URL user-info.
2. MEDIUM / misleading runtime status: `GET /api/status` returned `read_only: true`, although `POST /api/feedback` explicitly persists creator feedback. Repair: retain the `read_only` compatibility key with truthful value `false`, add `preanalysis_read_only: true`, `feedback_writes_local: true`, `feedback_requires_explicit_creator_confirmation: true`, `global_learning: false`.
3. Verification gap: R1.4 source tests existed but did not exercise the localhost Host/origin/feedback HTTP path. Repair: additive `source/tests/test_daemon_http_guard.py` with six isolated HTTP contract tests.

## Testing and status
- Authored 6 focused HTTP tests: status integrity, forbidden GET Host, forbidden POST Host with no local evidence write, forbidden cross-origin POST, successful localhost feedback+readback, malformed category HTTP 400.
- Execute from `PROJECTS/666TDI/source` with `python -m unittest tests.test_daemon_http_guard -v` or `python -m unittest discover -s tests -v`.
- Tests must not be marked PASS until actually executed in the exact checked-out revision. External browser/Windows acceptance remains open.
- Repair changes no Suno calls, no automatic song creation, no global learning, no foreign repository writes.
- Keep Source-Manifest source SHA256 / Git blob integrity verification separate from Python/host runtime verification.

## Tradeoffs
- HTTP calls without a Host header are rejected; normal modern browsers and HTTP/1.1 clients send one automatically.
- Browsers using a proxy or non-local hostname cannot call the local service; this is intentional.
- A localhost HTTP server without authentication is still accessible to processes on the same machine; this patch is hostname/origin hardening, not a user-authentication system.

## Handoff
Run the HTTP tests, verify the local browser from both `127.0.0.1` and `localhost`, and check real R1.4 feedback persistence. Preserve learning ledger and old R1.0–R1.3 outputs.
