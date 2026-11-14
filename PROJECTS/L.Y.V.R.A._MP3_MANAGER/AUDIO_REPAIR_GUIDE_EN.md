# AUDIO REPAIR — v2.34

Choose **WAV → MP3 REPAIR (A/B)** in the existing Audio Convert tab.
Select the clean original WAV and the problematic MP3 as reference.
Confirm the track match and create a separately named `REPAIRED.mp3` in
`_666MP3_REPAIR` beside the reference MP3. Both originals remain untouched.
Repair always uses Maximum Quality (48 kHz, 320 kbps, stereo, LAME,
no loudness normalization). A `*.mp3.quality.json` sidecar records hashes
and technical decode validation. Listen to A/B at matched playback level:
MP3 codec artefacts cannot be diagnosed or repaired reliably by decode tests alone.
Do not use a damaged MP3 as the repair source when a clean WAV exists.
