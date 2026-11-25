# 666 CHATBACKUP PC TOOL — additive R57 candidate (SOURCE TRANSFER PARTIAL)

**Native application authority:** 666 CHATBACKUP PC TOOL (original v1.10.5 -> R55 -> R56.3).  
**Integrated feature addon:** Chatback Import Studio R18.1 — separate engine/database.  
**Developer-only layer:** Universal Buildkit R01.11.3.  
**New candidate:** R57 share, inspector, image metadata and conversation tree routes added to R56.3 without overwriting Studio/Buildkit.

## GitHub publication gate
This branch is **NOT a complete source publication**. Full local validated candidate has 193 Python main tests and 128 Studio tests passing, plus 82 Python subtests. It is not a Windows-host acceptance or a public release. Do not promote this documentation checkpoint to Current.

**Never claim** the archive is fully published until the entire approved clear-source set has been uploaded, the remote Git tree has been enumerated and every file's content hash read back.

## Confirmed R57 regression hazard
The submitted R57 ZIP omits 184 files of the R56.3 archive, including all of `addons/chatback_import_studio/` and `development/universal_buildkit_R01_11_3/`. Ten overlapping source files differ. Treat R57 as a feature donor only.

## Source privacy
The three Scriptable backup exports (879 distinct message IDs) were studied locally. Their raw HTML/JSON, user chat content and the original historic ZIP/SQLite data are **not approved for public GitHub publication**. Exclude binary Python installers, wheels, private backup contents, and local databases from any public source tree.

## Deployment status
`PARTIAL · SOURCE_TRANSFER_PENDING · NO_PRODUCTION_MERGE · WINDOWS_HOST_READBACK_PENDING`
