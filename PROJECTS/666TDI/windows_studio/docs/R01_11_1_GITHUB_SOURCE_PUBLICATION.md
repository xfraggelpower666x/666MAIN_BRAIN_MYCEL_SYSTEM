# R01.11.1 — Source publication transport

This package adds a deliberately interactive, non-destructive GitHub publication helper. The ChatGPT GitHub connector can publish UTF-8 source but cannot upload the original PNG/WebP/ZIP bytes from the local sandbox through its available API shape. This helper is for use on the user's own Windows machine with Git installed and GitHub authentication configured.

1. Extract this complete ZIP locally.
2. Double click `PUBLISH_SOURCE_TO_GITHUB.bat` (separate from normal STARTEN.bat).
3. Review the explicit repository/branch scope and type `JA` to authorize.
4. The script checks every source SHA-256, clones only the isolated development branch, creates a pre-change backup branch, copies source files, commits/pushes without force, and verifies the remote branch SHA and every Git blob.

No production merge, no trigger activation, no foreign project rewrite, no secrets in files. If any SHA, scope, Git authentication or branch constraint fails, it stops rather than declaring success. Windows acceptance is outstanding.
