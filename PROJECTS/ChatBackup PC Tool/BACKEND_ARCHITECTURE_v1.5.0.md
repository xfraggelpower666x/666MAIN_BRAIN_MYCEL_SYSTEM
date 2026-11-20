# 666 ChatBackup Backend Architecture v1.5.0

## Ziel

v1.5.0 trennt den Chat-Import logisch in Transport, Parser, verlustarme Nachrichtenerhaltung, UI-/Copy-Feld-Analyse, Asset-Erkennung, Integritätsbewertung und Archivexport. Die bestehende Cyber-Neon-GUI und der Bildbrowser bleiben erhalten, arbeiten aber beim Share-Import über `ChatBackend`.

## Backend-ID

- `666.chatbackup.backend.v1`
- Backend-Version `1.0.0`
- App-Version `1.5.0`

## Pipeline

1. URL normalisieren und öffentliche `/share/`-/`/s/`-Route prüfen.
2. Share-HTML mit Retry und Browser-Headern laden.
3. Parser-Reihenfolge: React Flight (`streamController.enqueue`, `self.__next_f.push`, `__next_f.push`) -> `__NEXT_DATA__` -> statischer DOM-Fallback.
4. Parser-Versuche und Primärfehler als Provenienz protokollieren.
5. Sichtbare Nachricht als `renderedText` normalisieren.
6. Parallel `rawContent`, `rawMetadata`, Message-ID, `contentType`, Status und Recipient erhalten.
7. Chat-Assets und Asset-Pointer extrahieren und vorhandene Direkt-URLs konservativ anreichern.
8. `GenUI.copy(identifier)` statisch untersuchen. Nur literale `const`/`let`-Strings werden aufgelöst. Kein `eval`, keine Funktionsausführung.
9. Integritätsprofil erzeugen: Source, Raw Preservation, UI Bindings, Assets, Visual Parity.
10. Optional Original-Share-HTML im Speicher erhalten und im Portable-Paket komprimiert archivieren.

## Lossless Message Model

Jede strukturierte Nachricht kann enthalten:

- `message_id`
- `role`, `author`, `recipient`, `status`
- `created_at`
- `content_type`
- `text` / `renderedText`
- `raw_content`
- `raw_metadata`
- `copy_fields[]`
- `warnings[]`
- `assets[]`

`raw_content` und `renderedText` sind absichtlich getrennt. Das sichtbare Backup bleibt lesbar; gleichzeitig können spätere Backend-Versionen auf den ursprünglichen strukturierten Feldern neu aufbauen.

## Raw Source / Reparse

Bei aktiviertem Raw-Capture und Share-HTML <= 12.000.000 Zeichen wird die HTML-Quelle im Backend gehalten. Das Portable-ZIP kann daraus erzeugen:

- `source/conversation.raw.json`
- `source/parser_receipt.json`
- `source/share-source.html.gz`

`ChatBackend.reparse()` kann archiviertes Share-HTML später mit dem jeweils aktuellen Parser erneut auswerten.

## Sicherheitsmodell

- kein Ausführen von Chat-JavaScript
- kein `eval`
- dynamische Template-Ausdrücke bleiben `UNRESOLVED`
- kein künstliches Rekonstruieren nicht gelieferter Bildbytes
- kein Anspruch auf pixelgenaue ChatGPT-UI-Rekonstruktion
- private `/c/`-Links bleiben abgelehnt

## v1.5.2 Addendum — Structure Snapshot API

Das Backend stellt `structure_inspector_payload(chat)` bereit. Das Schema ist bewusst vom allgemeinen Machine Export getrennt, damit genau die im Struktur-Inspector sichtbare Semantik stabil archiviert, diffbar gemacht und unabhängig weiterverarbeitet werden kann.
