# R3 Integration Audit — homebrew-keyboard_leds

## Verified upstream evidence
- Repo: https://github.com/tomohiro/homebrew-keyboard_leds
- Branch: master; HEAD `a4456b266add7f797a78e5db5072a81641ff4ceb` (2017-11-23). Archived.
- `README.md`: macOS get/set Caps and Num Lock LED command.
- `keyboard-leds.rb`: Ruby Homebrew formula fetching separate `keyboard_leds.c` and building with macOS IOKit/CoreFoundation.
- GitHub license metadata: none. **No foreign source copied**.

## Decision
- KEEP: Python R1/R2 monitoring, 3 LED backend, SSD read/write visual signal, config schema 1.
- ADD: `klrw.manual` and `klrw.ledctl` for direct get/set interface and guarded Windows compatibility.
- REJECT: installing Homebrew, compiling Apple IOKit on Windows, pretending the LED is addressable independently of lock-key state.
- Hardware/Windows GUI live acceptance: READBACK_PENDING.
- No GitHub writes.
