# BLISTER TOY · R04 native regression update · 2026-11-22

Authority: PROJECTS/BLISTER_TOY_DESIGNER only, branch 666MAIN_BRAIN.
Reason: prior R04 current contained a test plan but no executable native regression suite.

## Preserved
Unmodified: app/index.html, reference_card.json, properties_card.json, language_card.json, all 19 placeholders, EN default / DE selectable, original R04 audit, runtime/cli.mjs and foreign projects.

## Added
- tests/test_native.mjs: 14 project-local Node built-in tests
- this regression report and pre-change recovery evidence

## Evidence
Baseline GitHub HEAD ac3f04d89f9ac303176e19b542bc7fd10382bc67.
Baseline project pointer 1a1893f8930fbed040eef8ba87a1cd900d59ab23.
Baseline tree: 15/15 tracked project file Git blobs matched pointer (direct GitHub tree readback).
Tests: 14/14 PASS on an isolated local fixture with byte-identical R04 app/cards and CLI Git blob; the fixture uses simplified project registry/handoff and pointer entries.
Test command after repository clone: `node --test tests/test_native.mjs`.
Fresh checkout integration and Windows host acceptance remain OPEN; do not count this fixture regression as a completed fresh checkout or ChatGPT host adoption.

## Publish contract
New body first, compare hashes with direct GitHub readback, project CURRENT_POINTER.json last; no mutation after pointer.
