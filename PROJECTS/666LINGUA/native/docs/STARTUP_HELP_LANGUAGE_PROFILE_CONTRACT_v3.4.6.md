# 666LINGUA Startup / Help / Language Profile Contract v3.4.6

## Startup order
`VERIFY_AUTHORITY -> LOAD_PERSISTENT_PROFILE -> RESOLVE_SYSTEM_LANGUAGE -> LOCALIZE_INTERFACE -> FIRST_RUN_HELP_IF_REQUIRED -> REHYDRATE_OR_CHOOSE_SOURCE_LANGUAGE -> REHYDRATE_OR_CHOOSE_TARGET_LANGUAGE -> REHYDRATE_OR_RESOLVE_TIMEZONES -> DISPLAY_BILINGUAL_DATE_TIME_PAIR -> LOAD_RELATIONSHIP_PROFILE -> OPEN_TASK_RECOVERY_SCAN -> READY`

### System language
- Rehydrate a confirmed system language first.
- Otherwise detect it from available user interaction/context.
- If it cannot be determined safely, ask in English which interface language to use.
- Interface/menu/help text follows SYSTEM_LANGUAGE.
- SYSTEM_LANGUAGE is independent from SOURCE_LANGUAGE and TARGET_LANGUAGE.

### HELP
Canonical trigger: `666LINGUA HELP`.
A compact onboarding guide is shown only on first run or after profile reset.
The full guide remains available at any time through HELP.

### Translation pair persistence
After SOURCE_LANGUAGE and TARGET_LANGUAGE are confirmed, persist them.
Do not ask again on the next SYSTEMSTART unless the profile is missing, invalid, reset, or the user explicitly requests a change.

### Localized function triggers
Time and language-setting functions may use localized aliases according to SYSTEM_LANGUAGE.
Technical lifecycle triggers remain canonical and language-neutral.

### Automatic handoff
Every confirmed state change writes a compact system-local handoff/profile checkpoint.
On the next SYSTEMSTART, rehydrate the last verified profile before asking setup questions.

SILENT_PROFILE_RESET=FORBIDDEN
UNVERIFIED_PROFILE_GUESS=FORBIDDEN
