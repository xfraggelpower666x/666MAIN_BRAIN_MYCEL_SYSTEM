# Recovery Guide
1. Restore the TDH SHACHIVITI wrapper.
2. Resolve SOURCE_VAULT_PROVIDER_FOLDER_ID and verify every provider object by file name, size and SHA-256.
3. For native SHACHIVITI recovery, use the v1.0.76.1 chain package; rebuild/reference v1.0.49 and process v1.0.50 through v1.0.76 in order.
4. Preserve v1.0.35.1 as historical provenance; never promote it over v1.0.76.
5. Treat v1.0.62, v1.0.73 and v1.0.74 packages as supporting source evidence, not later master authority.
6. Do not infer a missing native source SYSTEM_ID.
