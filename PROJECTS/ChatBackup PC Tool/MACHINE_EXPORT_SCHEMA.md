# Maschinenexport-Schema — 666.chatbackup.machine.v1

## Version

`schemaVersion=1.3.0` ab ChatBackup v1.5.0. Das Schema bleibt rückwärts unter derselben Familie, ergänzt aber verlustarme Message-Quelldaten, Copy-/UI-Felder, Parser-Provenienz und Raw-Source-Metadaten.

## Top-Level

- `schema`, `schemaVersion`, `tool`, `toolVersion`, `exportedAt`
- `title`
- `source`
- `sourceCapture`
- `conversation`
- `renderedContent`, `renderedContentSha256`
- `messages[]`
- `assets[]`
- `assetSelection`
- `localAssets[]`

## Message-Felder v1.2.0

- `index`
- `id`
- `role`, `author`, `recipient`, `status`
- `createdAt`
- `contentType`
- `renderedText`
- `rawContent`
- `rawMetadata`
- `copyFields[]`
- `warnings[]`
- `assets[]`

`rawContent` und `rawMetadata` werden nicht ausgeführt, sondern nur archiviert.

## Copy-/UI-Felder

Jeder Eintrag kann enthalten:

- `identifier`
- `label`
- `resolved`
- `text`
- `utf16Length`

Nur statisch deklarierte literale Strings werden rekonstruiert. Dynamische `${...}`-Templates bleiben ungelöst.

## Source Capture

`sourceCapture` enthält u. a. Status, HTML-Zeichenanzahl, SHA-256, Parser-Versuche, Primärfehler und `reparseReady`.

## Integrität

`conversation.integrity` trennt:

- `sourceStatus`
- `rawPreservation`
- `uiBindings`
- `assets`
- `visualParity=NOT_CLAIMED`
- Zähler für übersprungene/unvollständige Nachrichten und Copy-Felder

## Portable Package

Zusätzlich zu TXT/MD/JS/JSON/JSONL und Assets kann `source/` enthalten:

- `conversation.raw.json`
- `parser_receipt.json`
- `share-source.html.gz`

Damit kann ein archivierter Chat mit späteren Parser-Versionen erneut interpretiert werden, sofern die Original-Share-HTML im Export enthalten war.

## Struktur-Inspector-Snapshot (v1.5.2)

Neben dem allgemeinen Maschinenexport existiert das eigenständige Schema `666.chatbackup.structure-inspector.v1` (`schemaVersion=1.0.0`). Es spiegelt systematisch die Inspector-Inhalte: Summary, Integritätsprofil, Parser-Provenienz und `messages[]` mit ID, Rolle, Autor, Recipient, Status, Content-Type, Unix-Zeit, Copy-Feldern, Warnungen, Raw Content, Raw Metadata, Rendered Text und Assets. Portable Pakete speichern diesen Snapshot unter `source/structure_inspector.json`.


## v1.8.0 Gruppenchat-Erweiterung

`conversation` enthält zusätzlich `conversationType`, `isGroupChat`, `groupChatEvidence`, `participantCount` und `participants[]`. Nachrichten enthalten die Participant-Felder `participantId`, `participantDisplayName`, `participantKind`, `participantUsername` und `participantResolution`. Fehlende Identität bleibt `UNRESOLVED`.
