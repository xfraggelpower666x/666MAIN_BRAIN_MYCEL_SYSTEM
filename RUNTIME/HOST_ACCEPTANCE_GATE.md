# HOST ACCEPTANCE GATE

OWNER=666MAIN BRAIN MYCEL SYSTEM
PURPOSE=SEPARATE_REPO_SOURCE_SUCCESS_FROM_FRESH_CHAT_HOST_BEHAVIOR

## Layers

SOURCE = repository artifacts and readback
DELIVERY = plugin/runtime package delivered to host
ADOPTION = host exposes the intended native skill/trigger
HOST = fresh-chat direct trigger actually resolves and executes expected read-only/update path

SOURCE_PASS_NE_DELIVERY_PASS=TRUE
DELIVERY_PASS_NE_ADOPTION_PASS=TRUE
ADOPTION_PASS_NE_HOST_PASS=TRUE

## Host acceptance cases

SYSTEMSTART
STATUS
HELP
WEITER
NEW_CHAT
VORNE
DASHBOARD
FUCK_HORST
UPDATE

Each case records:
- direct trigger
- expected native owner
- expected repo pointer resolution
- expected write authority
- observed behavior
- observed source
- classification
- evidence timestamp when available

## Classes

HOST_VERIFIED
HOST_PARTIAL
HOST_UNAVAILABLE
HOST_DRIFT
HOST_READBACK_PENDING

FINAL_COMPLETION_REQUIRES=HOST_VERIFIED_OR_EXPLICITLY_CLASSIFIED_HOST_ONLY_BLOCKER
