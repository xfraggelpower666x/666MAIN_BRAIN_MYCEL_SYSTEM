# Windows Host Acceptance Protocol — v1.10.5

Run `VERIFY_WINDOWS_HOST_ACCEPTANCE.bat` on the real Windows 10/11 host.

The workflow runs three governed gates:

1. release-integrity verification;
2. real Windows GUI/runtime readback of the released PYw entry point, including the Browser-Recovery dialog;
3. live public ChatGPT Share fetch → parser → Markdown/JSON/JSONL/Structure/Parser-Receipt export → exact byte readback and message-count readback.

A Windows host gate is closed only when the receipt reports:

`WINDOWS_HOST_ACCEPTANCE_PASS`

The receipt is written below `runtime_readback/host_acceptance_*/windows_host_acceptance_receipt.json`.

A fixture or non-Windows PASS is useful regression evidence but does **not** close the Windows host gate.

All three probes use the Python executable selected by the bootstrap. The source acceptance does not launch the compiled EXE. The Browser-Recovery check opens the tool dialog and does not access the browser or clipboard.
