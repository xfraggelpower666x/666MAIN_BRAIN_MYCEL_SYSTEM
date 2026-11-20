# 666LINGUA Startup Language Contract v3.4.6

SYSTEM_LANGUAGE_FIRST=TRUE
SYSTEM_LANGUAGE_REHYDRATE_BEFORE_DETECT=TRUE
SYSTEM_LANGUAGE_AUTO_DETECT=TRUE
SYSTEM_LANGUAGE_CONFIDENCE_REQUIRED=TRUE

## Unknown-language fail-safe
If SYSTEM_LANGUAGE cannot be determined with sufficient confidence:

1. Set temporary interface language to English BEFORE asking anything.
2. Do not show German setup instructions.
3. Ask in English:

   "I could not determine your preferred system language.
   Which language should I use for the 666LINGUA interface?"

4. Accept a language name or locale.
5. Set SYSTEM_LANGUAGE to the confirmed value.
6. Immediately localize all subsequent menus, help text, prompts, and setup instructions.

UNKNOWN_SYSTEM_LANGUAGE_TEMP_INTERFACE=en
UNKNOWN_SYSTEM_LANGUAGE_QUESTION_LANGUAGE=en
GERMAN_FALLBACK_FOR_UNKNOWN_LANGUAGE=FORBIDDEN
ASK_BEFORE_ENGLISH_SWITCH=FORBIDDEN
ENGLISH_SWITCH_BEFORE_QUESTION=REQUIRED

## Separation of concepts
SYSTEM_LANGUAGE is the interface/menu/help language.
SOURCE_LANGUAGE is the language to translate from.
TARGET_LANGUAGE is the language to translate into.
TIMEZONE is independent from language and must be resolved separately.

## First-run order
LOAD_STATE
→ REHYDRATE_SYSTEM_LANGUAGE_IF_PRESENT
→ ELSE DETECT_SYSTEM_LANGUAGE
→ IF UNRESOLVED SWITCH_INTERFACE_TO_ENGLISH
→ ASK_SYSTEM_LANGUAGE_IN_ENGLISH
→ LOCALIZE_INTERFACE_TO_CONFIRMED_SYSTEM_LANGUAGE
→ SHOW_FIRST_RUN_HELP
→ CHOOSE_OR_REHYDRATE_SOURCE_LANGUAGE
→ CHOOSE_OR_REHYDRATE_TARGET_LANGUAGE
→ RESOLVE_OR_REHYDRATE_TIMEZONES
→ DISPLAY_LOCALIZED_DATE_TIME_PAIR
→ READY
