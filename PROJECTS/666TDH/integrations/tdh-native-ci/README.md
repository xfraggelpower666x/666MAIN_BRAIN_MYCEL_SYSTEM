# 666TDH · Repo-native Regression CI (Scope R1)

Status: CI_ENTRYPOINT_READY / GITHUB_ACTIONS_ACTIVATION_WRITE_BLOCKED

Aktuelle native Schreibautorität: PROJECTS/666TDH im Branch 666MAIN_BRAIN.
Das Skript tools/ci_validate.py verwendet das vorhandene native verify_and_backup.verify() und tdh.Current,
prüft alle SHA-256-Bindungen des Root-Pointers, 5 Childs, 9 Daemon-Routen, die HOLDs und bei vorhandenem R10
den nativen Audit + Return-Receipt. Anschließend laufen die bestehenden Python-Tests und die neuen Negativtests.
Es behauptet keinen ChatGPT-Host-PASS, keine FSE-Vault-Prüfung und keinen CLIC-ACK.

## GitHub Actions (noch nicht aktiviert)

GitHub Actions liest Workflow-Dateien nur unter .github/workflows/ am Repository-Root.
Die TDH-Authority setzt ALLOWED_WRITE_ROOT=PROJECTS/666TDH, weshalb ein gewöhnliches 666TDH UPDATE
keinen solchen Workflow installieren darf. Die funktionsfähige, aber nicht aktive Vorlage liegt unter
integrations/tdh-native-ci/666tdh-native-regression.workflow-template.yml.
Eine separate, ausdrücklich autorisierte Repository-Governance-Transaktion muss diese Vorlage nach Prüfung
unter .github/workflows/666tdh-native-regression.yml veröffentlichen, testen und readbacken.
Keine Änderung an PFS, CLIC, LYVRA, anderen Project-Roots oder bestehenden Workflows.

## Ausführung im vollständigen Git-Checkout

python -B PROJECTS/666TDH/tools/ci_validate.py --expected-head "$(git rev-parse HEAD)"

Status PASS_REPO_NATIVE_REGRESSION_NO_HOST_ASSERTION ist nur nach echten Ausführungstests zulässig.
CURRENT_POINTER.json ist die letzte Mutation einer nativen TDH-Update-Transaktion.
