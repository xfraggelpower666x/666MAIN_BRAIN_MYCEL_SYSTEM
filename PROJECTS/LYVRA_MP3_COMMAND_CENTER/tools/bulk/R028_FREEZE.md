# R02.8 candidate freeze — local integration only
Base: 3595f179e7b0d875d94dea71c2582c282d8873bd.
Additive binary_readback.py, controlled_release.py, test_controlled_release.py.
Audit: R02.7 review is inventory, not authorization; R02.6 approval gate did not bind SHA-256 or fresh archive review. New wrapper requires both and holds diagnostic files with detected path/credential markers. Existing modules unchanged. Independent fresh Git object store verifies commit, tree entry, SHA-1 and SHA-256 of selected bytes. Local test fixture only; real GitHub binary byte readback remains pending (DNS unavailable). No public assets authorized.
Regression: Python 3.13.5, Git 2.47.3; 20 tests passed (12 existing + 8 new), command `python -m unittest test_publish_resume test_asset_review test_controlled_release -v`. See R028_REGRESSION.txt.
Archive byte validation: mp3 122/122, dj 70/70, restore 66/66, boot 50/50. No mismatches. 263 originals on repository base; 45 held.
FFmpeg/FFprobe both contain gyan.dev and --enable-gpl markers, no --enable-nonfree marker found. Exact build and corresponding source/license delivery unresolved; no publication.
Restoration requirements already include PyWavelets and sounddevice; both absent in current Python environment. Isolated install attempted, no PyWavelets distribution available. DSP and Windows host acceptance open. No fake dependencies.
Freeze scope: tested local candidate modules only, not production or entire application. Next: binary-capable real GitHub readback, independently documented asset approval and Restoration host dependency resolution. No ZIP publication or production promotion.
