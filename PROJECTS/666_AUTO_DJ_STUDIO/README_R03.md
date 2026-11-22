# 666 AUTO-DJ STUDIO — R03 incremental source migration
The live source remains in PROJECTS/666_AUTO_DJ_STUDIO on branch 666MAIN_BRAIN.
R03 ports original PowerShell title/family/energy/group/block/shuffle planning to isolated Python module `engine/legacy_planner.py`. **Not connected to actual batch render yet.**
Use `BUILD.bat`: CHECK / DEPS / TEST / RUN / PORTABLE / SETUP / ALL.
On the builder, provide original `666_AUTO_DJ_R02_WINDOWS_ABNAHME_GATE_R03.zip` in `tools/source/` or the project root. The build script extracts SHA256-verified FFmpeg and FFprobe into resources. End-user binaries are intended to contain the required runtimes; no completed Windows package has been verified yet.
Build prerequisites may be installed through winget. Version upgrades, offline bootstrap and lockfile review remain open.
Read docs/PORT_R03.md. Full R03 feature parity, Windows runtime, audio and installer verification remain blocked.
