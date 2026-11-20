# Scriptable iPhone Companion — PC Integration v1.10.2

## Current companion

- Mobile version: `1.0.7`
- Current ZIP: `mobile_scriptable/666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.7.zip`
- Standalone and embedded ZIP must remain byte-identical.
- Previous v1.0.6 and v1.0.0 packages remain in `mobile_scriptable/history/`.

## New runtime evidence path

Scriptable v1.0.7 adds:

- seven-check offline self-test;
- non-destructive public-share compatibility probe;
- JSON reports copied to clipboard and written through Scriptable FileManager;
- Flight/SSR/source-fingerprint diagnostics.

These tools reduce the remaining iPhone gate to a real-device readback rather than more static inference.

## No PC parser replacement

PC v1.10.2 preserves the v1.10.1/v1.10.0 direct parser and Browser-Recovery implementation. The integration change is additive and companion-scoped.
