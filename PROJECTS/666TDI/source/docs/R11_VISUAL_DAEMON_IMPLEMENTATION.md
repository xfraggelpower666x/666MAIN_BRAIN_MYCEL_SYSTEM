# 666TDI R1.1 – Native Visual Daemon

## Real implementation
This release provides a local Python 3.10+ HTTP server and a dependency-free Neon-Cyber browser UI, using the existing R0.9/R1.0 music engines directly. No second composer or musical authority is introduced.

Files:
- `source/engine/daemon_cli.py`: localhost-only daemon and read-only preanalysis API.
- `source/engine/daemon_static/index.html`: responsive control center, device preflight, creator intent intake, function relationships, emergences, collision hypotheses, creator decision cards, JSON export.
- `source/tests/test_daemon.py`: focused device, engine, non-mutation and UI contract tests.
- `source/START_666TDI_DAEMON.bat`: Windows launcher (Python required).

## Start
From `PROJECTS/666TDI/source`:
```bash
python -m engine.daemon_cli --port 8766
```
Then open `http://127.0.0.1:8766` in a web browser.

Windows: double-click `START_666TDI_DAEMON.bat`.

## Workflow
1. Creator chooses iPhone Suno App or PC Suno Browser. No silent default.
2. Creator enters musical intent. This can include voice, LOW/MID/HIGH, story, lyrics, arrangement, exclusions and optional BPM.
3. Native R0.9 and R1.0 analyze the submitted intent. No track creation or renderer execution.
4. The UI derives function evidence, relationships and emergent-effect hypotheses from the returned results.
5. Creator selects Preserve, Adapt or Reject for individual recommendations.
6. Creator exports the read-only analysis and choices as a local JSON download, or copies decision text.

## Trust boundaries
- Service bound only to 127.0.0.1. No cloud or Suno API calls.
- Payloads are JSON-limited and constrained to known musical fields.
- No tokens/secrets or real audio are requested; no persistent server-side track state.
- Creator decisions remain browser-memory only until manually exported.
- Built-in content is displayed as text; creator text is never inserted as executable HTML.
- Field availability, renderer-specific prompts, model parameters and host/clipboard acceptance are outside this R1.1 delivery.
- Rules provide explanatory hypotheses, not validated musical truth.
- Audio evaluation remains optional.
- No LYVRA or other foreign authority is activated, merged or modified.

## Validation
Run `python -m unittest discover -s tests -v`. The release includes authored tests, but the repository publication by itself does not certify execution or host-level browser acceptance.

## Next steps
R1.2 should consume the same API and add deeper graphical arrangement/timeline preanalysis. R1.3 should add verified per-device renderer adapters without changing the common music engine. R1.4 remains creator-reviewed evidence learning.
