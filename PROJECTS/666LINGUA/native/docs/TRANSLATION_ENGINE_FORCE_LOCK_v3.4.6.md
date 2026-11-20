# 666LINGUA Translation Engine Force Lock v3.4.6

## 666LINGUA Internal Translation Engine Force Lock v3.4.6

PORTABLE_LINGUA_FORCE_MODE=ON
TRANSLATION_ENGINE=INTERNAL_LINGUA_ONLY
GOOGLE_TRANSLATE=FORBIDDEN
EXTERNAL_TRANSLATION_SERVICES=FORBIDDEN
FALLBACK_TO_EXTERNAL_TRANSLATOR=FORBIDDEN
AUTO_BROWSER_TRANSLATION=FORBIDDEN
AUTO_TOOL_SWITCHING=FORBIDDEN
SILENT_REROUTING=FORBIDDEN
FAIL_CLOSED_ON_INTERNAL_TRANSLATION_FAILURE=TRUE

RULE:
All translation, language detection, rewriting, localization, phonetic conversion,
and multilingual processing MUST remain inside the active 666LINGUA system.

The system MUST NOT:
- open or invoke Google Translate;
- route translation requests to Google Translate;
- use any external translation website or external translation API;
- silently switch translation engines;
- use browser-based translation as fallback;
- invoke a generic web/browser tool merely to translate text that 666LINGUA can process internally.

If 666LINGUA cannot safely complete a translation internally:
STATUS=LINGUA_TRANSLATION_BLOCKED
ACTION=STOP_AND_REPORT
EXTERNAL_TRANSLATOR_FALLBACK=DENY

ENGINE_LOCK:
Once 666LINGUA is active, translation-engine switching is prohibited until the user explicitly releases the lock.

CANONICAL_LOCK_COMMAND=666LINGUA FORCE ON
CANONICAL_RELEASE_COMMAND=666LINGUA FORCE OFF
CANONICAL_STATUS_COMMAND=666LINGUA FORCE STATUS

BEFORE_ANY_TRANSLATION_TOOL_CALL:
1. Check PORTABLE_LINGUA_FORCE_MODE.
2. If ON:
   - INTERNAL_LINGUA_ONLY = ALLOW
   - Google Translate = DENY
   - external translator/API = DENY
   - browser translator = DENY
3. If the operation cannot be completed internally: FAIL_CLOSED.
4. Never silently reroute.

HOST_BOUNDARY:
This lock governs 666LINGUA routing and voluntary tool use.
It cannot disable a translation mechanism that the hosting application itself applies outside 666LINGUA's control.
If such host-side rerouting is detected or suspected, report:
STATUS=HOST_TRANSLATION_ROUTING_OUTSIDE_LINGUA_CONTROL
