# Feature — AUTH Wall Detection & Browser-Assisted Share Recovery v1.10.0

## Problem
Current ChatGPT Share responses can return a login/signup shell to direct automated HTTP retrieval while the same URL may still work in a normal authenticated browser. In that response, the conversation payload (`mapping`, `linear_conversation`, etc.) is absent.

## Repair
- explicit `AUTH_WALL_DETECTED` state before parser fallback
- conservative detection: login markers present + conversation payload markers absent
- no misleading unsupported-format error
- guided browser recovery from the user’s normal authenticated browser
- no cookie extraction, no login bypass, no browser credential access
- clipboard transcript is reconstructed with the existing fail-closed manual/group parser
- Structure Inspector opens after successful recovery
- warning that clipboard text cannot recreate image/file bytes

## Recovery flow
Direct Share Probe → conversation payload: normal parser
Direct Share Probe → AUTH wall: Browser Recovery → user copies visible transcript → structured reconstruction → Inspector → export
