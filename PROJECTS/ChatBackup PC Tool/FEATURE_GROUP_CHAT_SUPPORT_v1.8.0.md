# Group Chat / Multi-Participant Support — v1.8.0

## Ziel
Gruppen- und Mehrteilnehmer-Verläufe verlustärmer sichern, ohne Teilnehmeridentitäten zu erfinden.

## Strukturierte Share-Daten
Das Backend liest explizite Teilnehmerverzeichnisse aus bekannten Teilnehmer-/Mitgliederfeldern sowie explizite Teilnehmer-IDs oder Namen an Nachrichten. Es führt diese Informationen in `ChatParticipant` und den Participant-Feldern von `ChatMessage` zusammen.

## Gruppenchat-Erkennung
`conversation_type=group` wird nur gesetzt, wenn mindestens ein belastbarer Hinweis vorliegt: explizites Group-Flag/Conversation-Type/Group-ID oder mindestens zwei explizit unterscheidbare menschliche Teilnehmer.

## Manueller Import
Neben You/User/Benutzer/ChatGPT/Assistant erkennt der Manual-Parser wiederholte explizite Sprecherlabels wie `Alice:` und `Bob:`. Freie Namen werden erst aktiviert, wenn der Verlauf mehrere unterschiedliche Teilnehmerlabels enthält. Codeblöcke werden nicht als Sprecherzeilen interpretiert.

## Export
Machine JSON 1.3.0, JSONL, Raw Source und Structure Inspector 1.1.0 enthalten:
- `conversationType` / `isGroupChat` / `groupChatEvidence`
- `participants[]`
- pro Nachricht `participantId`, `participantDisplayName`, `participantKind`, `participantUsername`, `participantResolution`

## Fail-closed
Wenn Teilnehmerdaten fehlen, bleibt `participantResolution=UNRESOLVED`. Es werden keine Personen anhand von Reihenfolge, Stil oder Inhalt geraten.


## v1.8.1 Hardening
- Assistant-/Custom-GPT-Identitäten aus strukturierten Teilnehmerdaten bleiben erhalten.
- Teilnehmer werden primär nach stabiler ID dedupliziert.
- Normale Markdown-Überschriften in kopierten Antworten werden nicht mehr als Gruppenteilnehmer interpretiert.
- Markdown-Sprecherüberschriften werden nur an klaren Transcript-Grenzen akzeptiert.
