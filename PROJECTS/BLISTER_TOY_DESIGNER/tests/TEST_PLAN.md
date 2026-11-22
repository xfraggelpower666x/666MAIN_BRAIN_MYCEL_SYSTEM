# R04 project acceptance

Existing local R04 audit: `audit/AUDIT_R04.md`. Verify the application source exactly matches the locally frozen R04 source. Native smoke: `node runtime/cli.mjs SYSTEMSTART`, STATUS, WEITER, HELP, NEW_CHAT. Verify 19 variables, English default, German switch, one-pass substitutions, JSON import/export and no filesystem writes. Host fresh chat trigger adoption is OPEN until actually exercised; do not report it as PASS. Repository readback is verified separately after commit.
