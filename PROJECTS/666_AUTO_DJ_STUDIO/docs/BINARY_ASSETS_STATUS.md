# 666 AUTO-DJ STUDIO — Binary payload scope (2026-11-24)

The repository update publishes the complete UTF-8 source code from the user-confirmed working Electron R06.1 Continuity ZIP. The ZIP contains 69 entries: 38 text files and 31 original binary assets. The latter are NOT included in this GitHub source commit because a byte-exact binary transport into GitHub has not been completed.

Original local bundle: `666_AUTO_DJ_STUDIO_CONTINUITY_ELECTRON_R06_1_DIRECT_REPAIR.zip` (83 MiB). Keep it as the authoritative binary payload source until separately verified.

- 29 original cover images remain at `legacy/covers/` in the original ZIP; they are not yet published here.
- `tools/ffmpeg/ffmpeg.exe` SHA-256: `1a65d5b0b10d8d9a81d2824a3538046a40ed3607c906b335a166add87613f705` (101060096 bytes)
- `tools/ffmpeg/ffprobe.exe` SHA-256: `54b944d6095c4588d7548424d7acd5118390a9d4f01b1c92f841547fc9a7429c` (100853248 bytes)

The legacy `build/PROVISION_FFMPEG.ps1` is preserved from the older R04 project and can extract the verified tools from the original R03 archive if available. This does not substitute for the missing cover files.

Windows observation reported by the owner: Electron development launch now works after the direct R06.1 installer repair. Portable EXE, Setup and complete audio parity are not thereby proven.

Status: SOURCE_LIVE_BINARY_PENDING, NO_COMPLETE_PACKAGE_CLAIM.
