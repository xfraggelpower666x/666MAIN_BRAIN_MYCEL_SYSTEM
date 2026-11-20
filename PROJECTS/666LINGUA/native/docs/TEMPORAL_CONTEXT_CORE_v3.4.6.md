# 666LINGUA TEMPORAL CONTEXT CORE v3.4.6

STATUS=ACTIVE_MANDATORY
RUNTIME_DEPENDENCY=NONE
HOST_EXECUTION_MODEL=AI_NATIVE_REASONING
SOURCE_FRAMEWORK=GTCF_v1.2.0
SOURCE_FRAMEWORK_ROLE=PROVENANCE_ONLY

## Atomic temporal unit
A verified time conversion MUST treat the following as one unit:

DATE + TIME + IANA TIMEZONE

Rules:
- DATE_REQUIRED_FOR_VERIFIED_CONVERSION=TRUE
- TIME_REQUIRED=TRUE
- IANA_TIMEZONE_REQUIRED=TRUE
- UTC_NORMALIZATION=REQUIRED
- DST_RULE_RESOLUTION=REQUIRED
- HARDCODED_OFFSET=FORBIDDEN
- DAY_CHANGE_DETECTION=REQUIRED
- MONTH_CHANGE_DETECTION=REQUIRED
- YEAR_CHANGE_DETECTION=REQUIRED
- RELATIVE_DATE_REEVALUATION=REQUIRED

Language never implies timezone. If a timezone is not already confirmed in the persistent profile,
the host MUST resolve or ask for the missing region/timezone before claiming a verified conversion.

## Automatic behavior
After SOURCE_LANGUAGE and TARGET_LANGUAGE are confirmed:
1. Rehydrate SOURCE_TIMEZONE and TARGET_TIMEZONE if available.
2. If either timezone is unresolved, obtain the missing region/timezone.
3. Resolve current date/time for both zones.
4. Display both sides immediately in their respective selected languages/locales.
5. Persist the confirmed timezone pair.
6. Keep the temporal context active for later translations.

For every meaningful translation input, detect temporal expressions such as:
today, tomorrow, yesterday, tonight, this morning, this afternoon, this evening,
next morning, next day, weekdays, calendar dates, and clock times.

If conversion changes the receiving calendar day, semantic translation MUST preserve the
actual target-side temporal meaning. Example: source-side "tomorrow night" may become
target-side "the day after tomorrow morning".

## Explicit localized triggers
DE: 666LINGUA UHRZEIT
EN: 666LINGUA TIME
ES: 666LINGUA HORA
FR: 666LINGUA HEURE
IT: 666LINGUA ORA

All localized triggers route to ONE internal function:
TEMPORAL_CONTEXT_REQUEST

## Required explicit-trigger output
The response must include, when resolvable:
- source language/locale
- source absolute date and time
- source IANA timezone and current UTC offset
- target language/locale
- target absolute date and time
- target IANA timezone and current UTC offset
- current time difference
- calendar-day shift indicator
- DST-aware status

## Fail-safe
If date, timezone, or temporal reference cannot be resolved reliably:
TEMPORAL_CONTEXT_STATUS=OPEN
Never guess a verified conversion.
