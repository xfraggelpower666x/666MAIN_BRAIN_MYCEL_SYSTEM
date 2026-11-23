# R07 · Safe test execution and acceptance boundaries

## Automated, hardware-free test gate

Run `python scripts/run_resin3_acceptance.py` from the project root.
It runs the R06/R05 unit test modules by exact name patterns, *not* the
original 3DX manual hardware scripts that run at import and require command
line arguments, Windows hardware, network streams, or driver installation.

The GitHub workflow `.github/workflows/666streamtranscoder-r07.yml` runs
the same selection on a headless Ubuntu Python 3.11 runner. Compilation
checks also cover the project package. Never interpret a passing CI unit
test as a Windows WASAPI, physical cable, portable installer, or live provider
certification.

## R08 headless real streaming gate

The script `tests/test_e2e_synthetic.py` generates two local stereo WAV tones and starts
the original FFmpeg decoder/encoder and built-in listener server, strictly bound
to 127.0.0.1. It requests audio from the HTTP listener, checks both a
normal automatic fade and the Skip fade, keeps the same encoder and HTTP
connection, and decodes received MP3 back to audible PCM.

Run `python -m unittest discover -s tests -p 'test_e2e_synthetic.py' -v`.
This confirms a real local encode/decode/network path **only if the job passes**.
It does not test a physical sound card, WASAPI, or real remote broadcast server.

## Local end-to-end acceptance (Windows)

Use an isolated local Icecast/Shoutcast mock server, finite tone/audio source,
and a local listener to verify a decoded stream is re-encoded and delivered.
Keep the existing encoder alive across playlist transitions and verify the
remote receiving socket never reconnects during Skip/Crossfade. Check that
monitor Play/Stop and local monitor gain do not change MP3 output bytes or
disconnect the server. Confirm audio devices by endpoint ID to guard against
virtual-cable feedback and device-name duplicates.

Do **not** automatically run `tests/test_engine.py`,
`tests/test_local_server.py`, `tests/test_app_capture.py` or
`tests/test_app_broadcast.py`: those are original 3DX manual scripts, not
unittest-discovery-safe tests. No public broadcaster login or physical driver
installation is performed by the headless CI gate.

## Acceptance record

- Repository publication and Git readback: requires a current commit/tree/blob check.
- Python compilation + headless contract suite: verified only after an execution receipt.
- Windows WASAPI capture: OPEN pending Windows execution.
- Physical monitor / VB-CABLE: OPEN pending device-specific execution.
- Shoutcast/Icecast end-to-end: OPEN pending real or local isolated socket tests.
- Portable EXE / installer: OPEN pending Windows build artifact and execution.
