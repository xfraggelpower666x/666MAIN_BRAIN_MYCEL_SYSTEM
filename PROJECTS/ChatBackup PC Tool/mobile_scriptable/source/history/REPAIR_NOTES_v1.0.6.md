# Repair Notes — v1.0.6

## Problem

ChatGPT shared links were observed to alternate between at least two live delivery families:

- structured React-Flight / legacy conversation payloads;
- server-rendered transcript HTML with `data-conversation-transcript` and `data-message-role`.

A WebView-only SSR fallback was not sufficient because Scriptable may not expose the same rendered DOM that is present in the fetched source.

## Repair

- Added a direct raw-HTML SSR transcript parser before all WebView fallbacks.
- Bounded message discovery to the verified `data-conversation-transcript` root.
- Added explicit assistant/user body selectors.
- Preserved stable message IDs when present.
- Added direct HTTP(S) image extraction from SSR message segments.
- Kept human participant identity unresolved when the source supplies only a role.
- Expanded failure diagnostics with source-format fingerprints.
- Preserved React-Flight, legacy, manual/group, export, image, language and help paths.

## Regression policy

No existing parser family was removed or replaced. The new path is additive.
