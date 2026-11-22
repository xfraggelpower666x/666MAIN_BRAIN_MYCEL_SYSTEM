# R03 migration and build audit — 2026-11-22
Evidence source: user-provided 666_AUTO_DJ_R02_WINDOWS_ABNAHME_GATE_R03.zip, extracted tool.ps1.
Mapped source functions: Clean-Title (~149), Get-FamilyName (~170), Build-VariantCatalog (~874), Build-BalancedPlaylistBlocks (~909), Get-ArtistName (~991), Get-EnergyBucket (~1006), Optimize-BlockOrderHardcore (~1016), Optimize-BlockOrder (~1156).
New source: engine/legacy_planner.py and tests/test_legacy_planner.py.
Observed test evidence: original local planner implementation 13/13 Python unittest checks PASS; published code requires independent runtime readback. Planner is not connected to end-user Electron UI or a complete processing job.
Non-equivalence: original sort uses Get-Random; new planner accepts deterministic Random seed, yielding valid but not necessarily byte-for-byte identical order. No audio processing proven.
Build: new build/PROVISION_FFMPEG.ps1 extracts embedded binaries from owner-provided R03 ZIP with SHA256 values. It does not download unknown FFmpeg binaries. The source archive must be supplied on the build PC under tools/source/ or project root. Final package is designed to embed both binaries.
Still open: cover rotation, metadata, original profiles, full audio feature parity, true Windows direct run, portable and NSIS package execution, security review and final production freeze.
No project outside PROJECTS/666_AUTO_DJ_STUDIO may be modified.
