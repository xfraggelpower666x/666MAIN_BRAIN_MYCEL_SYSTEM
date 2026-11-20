# 666LINGUA Startup Disclosure Contract v3.4.6

## 666LINGUA Startup Disclosure Contract v3.4.6

FORCE_LOCK_DEFAULT=ON
FORCE_LOCK_DISCLOSURE_AT_START=REQUIRED
TRIGGER_OVERVIEW_AT_START=REQUIRED
UNKNOWN_SYSTEM_LANGUAGE_STARTUP_LANGUAGE=en
ENGLISH_FIRST_WHEN_SYSTEM_LANGUAGE_UNRESOLVED=REQUIRED
GERMAN_FALLBACK_WHEN_SYSTEM_LANGUAGE_UNRESOLVED=FORBIDDEN
ASK_SYSTEM_LANGUAGE_ONLY_AFTER_ENGLISH_STARTUP_SAFETY_NOTICE=TRUE

STARTUP_PRESENTATION_ORDER:

1. Present 666LINGUA identity and current version.
2. Resolve or rehydrate SYSTEM_LANGUAGE.
3. If SYSTEM_LANGUAGE is confirmed:
   - localize the complete startup presentation to that language.
4. If SYSTEM_LANGUAGE is unresolved:
   - immediately switch all visible startup output to English;
   - do not show German setup or safety instructions;
   - present the Force Lock status and essential trigger help in English;
   - then ask in English which system language should be used.
5. Show Force Lock status directly after the translator introduction.
6. Explain that the lock is ON by default.
7. Explain the three Force Lock commands.
8. Show the essential 666LINGUA command overview.
9. Rehydrate or resolve translation languages/locales/timezones.
10. Enter READY state.

MANDATORY_STARTUP_FORCE_LOCK_NOTICE_EN:

"Translation Engine Force Lock: ON.
666LINGUA is currently restricted to its internal translation engine.
Google Translate, external translation services, browser translation fallback,
silent rerouting, and external translation fallback are blocked by 666LINGUA.
Commands:
- 666LINGUA FORCE ON
- 666LINGUA FORCE OFF
- 666LINGUA FORCE STATUS"

MANDATORY_STARTUP_TRIGGER_OVERVIEW_EN:

"Essential commands:
- 666LINGUA SYSTEMSTART — start or rehydrate 666LINGUA
- 666LINGUA STATUS — show system status
- 666LINGUA HELP — show help and commands
- 666LINGUA UPDATE — run the controlled update cycle
- 666LINGUA FORCE ON — enforce internal-only translation
- 666LINGUA FORCE OFF — release the internal-only routing lock
- 666LINGUA FORCE STATUS — show Force Lock status
- 666LINGUA TIME — show temporal context
- 666LINGUA LANGUAGES — show or change language configuration"

UNKNOWN_LANGUAGE_RULE:
If the system language cannot be determined with sufficient confidence, the first visible
startup safety/help output MUST be English. Only after the user confirms a system language
may the system localize the startup interface to another language.

PORTABLE_REQUIREMENT:
The Portable package MUST implement the exact same startup disclosure behavior.
It MUST NOT suppress the Force Lock notice or trigger overview.
The Portable first-run state therefore begins with Force Lock ON.
