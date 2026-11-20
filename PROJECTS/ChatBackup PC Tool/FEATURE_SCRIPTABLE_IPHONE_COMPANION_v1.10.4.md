# Scriptable iPhone Companion Integration — PC Tool v1.10.4

Current companion: `666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.8.zip`.

## Additive change

- v1.0.8 adds one-step real-device host acceptance: live Share fetch → parser → exports → FileManager readback → machine receipt.
- PC v1.10.4 adds the matching Windows host-acceptance receipt path.
- Existing PC import logic is preserved.
- Historical mobile packages remain under `mobile_scriptable/history/`.

## Host authority

Only receipts generated on the real target host can close a host gate:
- Windows: `WINDOWS_HOST_ACCEPTANCE_PASS`
- iPhone: `HOST_ACCEPTANCE_PASS`
