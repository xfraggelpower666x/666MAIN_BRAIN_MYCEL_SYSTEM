# Verification report — v2.34

**Source:** original v2.33 zip. No PFS/GitHub writes.

| Test | Result |
| --- | --- |
| Python syntax of app | PASS |
| FFmpeg libmp3lame detector | PASS on Linux host |
| Synthetic WAV→MP3→ID3→decode full | PASS |
| Repair WAV→new MP3 with damaged reference | PASS |
| Original WAV and reference MP3 SHA256 unchanged | PASS |
| Per-file report hashes source, output, reference | PASS |
| Anti-normalization preset guard | PASS |
| Reject bad MP3 or incorrect duration | PASS |
| Real user Suno WAV eight-second **excerpt** converted | PASS |
| Full untouched real Suno WAV hash unchanged | PASS |
| Real user MP3 complete decode (343.992 s) | PASS |
| Tk GUI under Xvfb 1024x680 / 1450x900 / 1920x1080 | PASS |
| Windows portable EXE | NOT TESTED |
| Windows multi-monitor / DPI | NOT TESTED |
| Perceptual artifact A/B with matched WAV and MP3 | NOT TESTED |

**Interpretation:** Software integration and technical file integrity checked;
no claim of restored lost MP3 information or subjective artefact-free sound.
