# Struktur-Inspector JSON Schema — v1.0.0

Schema-ID: `666.chatbackup.structure-inspector.v1`

## Zweck

Der Snapshot bildet systematisch die Daten ab, die der Struktur-Inspector sichtbar macht. Er ist bewusst vom allgemeinen Machine Export getrennt und eignet sich für Archivierung, Diff, spätere Analyse und automatisierte Weiterverarbeitung.

## Top-Level

- `schema`, `schemaVersion`, `tool`, `toolVersion`, `exportedAt`
- `title`, `sourceUrl`, `shareId`
- `summary` — Parser, Nachrichtenanzahl, Copy-Feld-Statistik, Raw-Preservation, Source-Hash, Visual-Parity
- `integrity` — mehrdimensionales Integritätsprofil
- `parserProvenance` — Parser-Versuche, Primärfehler, Source-Capture-Status
- `messages[]` — vollständige strukturierte Inspector-Nachrichten

## Message-Felder

- `index`, `id`, `role`, `author`, `recipient`, `status`, `contentType`, `createdAtUnix`
- `copyFields[]`
- `warnings[]`
- `rawContent`
- `rawMetadata`
- `renderedText`
- `assets[]`

## Einzel-Nachrichtenexport

Die GUI kann eine ausgewählte Nachricht zusätzlich als `666.chatbackup.structure-inspector.message.v1` speichern. Der Message-Block ist derselbe wie im Gesamtsnapshot.

## Portable ZIP

Bei strukturierten Share-Chats wird der Gesamtsnapshot automatisch als `source/structure_inspector.json` gespeichert und im Package-Manifest mit Größe und SHA-256 aufgeführt.


## v1.8.0 Participants

Der Snapshot enthält `participants[]` sowie Gruppenchat-Zusammenfassung und Participant-Felder je Nachricht. Damit kann ein Gruppenverlauf inklusive Sprecherzuordnung separat archiviert und diffbar ausgewertet werden.
