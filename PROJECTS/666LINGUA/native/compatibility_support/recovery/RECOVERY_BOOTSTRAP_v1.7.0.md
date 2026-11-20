# LYVRA DOLMETSCHER RECOVERY BOOTSTRAP v1.7.0

## Trigger

```text
LYVRA DOLMETSCHER RESTORE
```

## Verbindlicher Ablauf

1. SYSTEM_ID und Namespace prüfen.
2. Sicherungsquelle bestimmen.
3. SHA-256-Manifest prüfen.
4. ZIP-CRC und Einträge prüfen.
5. Version mit lokalem Zustand vergleichen.
6. Neueren verifizierten Zustand niemals überschreiben.
7. Checkpoint und Register lesen.
8. Systemsprache, Modus, Locks, Queues und Task-Stack rehydrieren.
9. Restore-Audit ausführen.
10. Unterbrochene Vorgänge in ihrer verifizierten Reihenfolge fortsetzen.

## Paketimport-Abgrenzung

Ein tatsächlicher ZIP-Import startet den normalen Bootstrap, nicht automatisch den Recovery-Pfad. Recovery wird nur über den exakten Restore-Befehl oder eine eindeutig angeforderte Wiederherstellung aktiviert.

## Blockgründe

- falsche System-ID
- beschädigtes Manifest oder ZIP
- Hash- oder CRC-Fehler
- ältere Sicherung würde neueren Zustand überschreiben
- widersprüchliche Checkpoints
- unvollständiger Task-Stack

In diesen Fällen gilt `CONFLICT_QUARANTINE`; es wird kein PASS erfunden.

## Systemsprachen-Recovery

Eine gespeicherte Systemsprache wird nur bei verifiziertem Checkpoint wiederhergestellt. Fehlt sie, läuft dieselbe Host-/GPT-/Chat-Sprachauflösung wie beim Normalstart.
