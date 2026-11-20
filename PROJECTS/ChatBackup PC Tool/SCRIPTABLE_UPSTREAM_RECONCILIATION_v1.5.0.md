# Scriptable Upstream Reconciliation — 2026-10-19

## Ausgangspunkt

Der PC-Client entstand ursprünglich aus dem Scriptable-Share-Exporter, hat sich inzwischen aber eigenständig entwickelt. Der am 19.10.2026 direkt im Chat bereitgestellte neue Scriptable-Stand wurde deshalb als Upstream-Referenz bewertet, nicht als Master-Ersatz.

## Übernommen

- getrennte Erhaltung von Rohinhalt und gerendertem Text
- `rawContent` und `rawMetadata`
- Message-ID und `contentType`
- Parser-Primärfehler / Provenienz
- statische Copy-Feld-Erkennung rund um `GenUI.copy(identifier)`
- ungelöste dynamische Bindungen explizit markieren
- ehrliche Integritätssemantik: Source-Erfolg ist keine visuelle UI-Parität
- Raw-Source-Bundle für spätere Neuinterpretation

## Bewusst nicht zurückgebaut

Der PC-Parser bleibt stärker und unterstützt weiterhin mehrere React-Flight-Einstiegspunkte. Ebenfalls erhalten bleiben Maschinenexport, JSONL, Bildbrowser, selektive Asset-Sicherung, Portable ZIP, SHA-256/Byte-Readback und Windows-Bootstrap.

## PC-spezifische Weiterentwicklung über Scriptable hinaus

- `ChatBackend` als explizite Orchestrator-Schicht
- Reparse-API für archiviertes Share-HTML
- GZIP-Archivierung der Share-Quelle im Portable-Paket
- Struktur-Inspector in der GUI
- mehrdimensionale Integritätsprofile
- maschinenlesbarer Parser-Receipt
