# R03.2 Candidate Freeze

Status: CANDIDATE_FROZEN_HOST_SCOPE

Tested executable source commit: 57be79d44682a13202604a8a93e833709fdcc102
Tested tree: 914d876cb94bc6b941d0bacd24a970bf76b4aaab
GitHub Actions run: 45745949583 (attempt 1, success; 4/4 independent jobs).
Workflow: LYVRA MP3 R03 isolated acceptance
Windows job: 139661939059 — PASS.
Adapter job: 139661938893 — PASS.
Binary job: 139661939134 — PASS.
DSP job: 139661939215 — PASS.

Windows portable acceptance: Python 3.11.9 staged from the GitHub Actions Python toolcache; FFmpeg/FFprobe 7.1.1 staged from the Windows runner/Chocolatey source. SHA-256 values for Python, FFmpeg, FFprobe and the packaged executable are recorded in R032_HOST_EVIDENCE.json. Electron was packaged with `--win --dir --publish never`. The packaged application started with a visible window; Python/DSP imports, FFmpeg and FFprobe version probes, the original MP3 engine probe (`MP3_READY`), and HUD title plus `#choose` / `#restore` selectors passed. The smoke receipt reported `packaged=true` and `visible=true`.

Regression: Windows Node 10/10; adapter Node 10/10; Python 26/26. Offline DSP STFT, Wavelet and Both all passed on the synthetic 3-second stereo fixture (132300 frames, 2 channels, 44100 Hz); source preservation PASS. Provider binary test passed for a 9-byte synthetic fixture.

Recovery backup: `backup/lyvra-mp3-r032-tested-57be79d`, direct readback at tested commit 57be79d44682a13202604a8a93e833709fdcc102.

This freeze binds executable source to the tested commit above. The later documentation-only freeze commit does not alter executable code and is not represented as a new CI run.

Limitations: unpacked Windows x64 package only; no installer or public release artifact; no manual end-user workflow test; physical audio output not tested; synthetic DSP fixture does not establish perceptual restoration quality; FFmpeg distribution licensing review remains separate; 45 original source files remain HOLD. No ZIP publication and no production promotion.
