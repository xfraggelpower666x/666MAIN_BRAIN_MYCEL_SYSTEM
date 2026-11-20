# Bilingual UI / Language Persistence — v1.6.0

## Policy

- First-start default: `English` (`language=en`).
- Supported UI languages: `English`, `Deutsch`.
- The selection is available directly in the left navigation.
- The selected language is persisted in the normal application settings and restored on the next start.
- Switching language rebuilds the visible main interface immediately while preserving the current editor text, URL, title and loaded chat state.

## Help

The left navigation contains `Help / Hilfe`. The integrated manual exists in both languages and explains the complete normal workflow, Structure Inspector JSON, chat images, Portable ZIP, shortcuts and known limitations.

## Compatibility

No chat schema, parser, archive, image-selection or backend contract was removed or renamed for this feature.
