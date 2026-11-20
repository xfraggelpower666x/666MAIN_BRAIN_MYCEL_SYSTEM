# Device Acceptance Plan v1.7.0

## Zielplattformen

- iOS
- Android
- Desktop
- Web
- WhatsApp-Share
- generisches Messenger-Share
- Clipboard

## Testphasen

### A. Contract simulation

Prüft Schema, getrennte Ausgaben, unveränderte Übersetzung und Copy-Safety.

### B. Real device input

- Diktat mit Nebengeräuschen
- abgebrochene Wörter
- Wiederholungen
- Wechsel zwischen Tastatur und Mikrofon
- lange Spracheingaben
- Korrektur einer bereits diktierten Nachricht

### C. Share behavior

- nur Übersetzung teilen
- Companion separat teilen
- Markdown-Fallback
- Emoji-Erhalt
- Zeilenumbrüche
- geschützte Tokens
- sehr lange Nachrichten

### D. Privacy

- kein Secret im Log
- Session-Forget
- Clipboard-Clear-Hinweis
- keine stillen Exporte

## Pass-Kriterium

Eine Plattform erhält erst `VERIFIED`, wenn ein realer Testreport mit Gerät, OS-Version, App, Datum,
Testfällen und Readback vorliegt. Bis dahin bleibt sie `NOT_PERFORMED`.
