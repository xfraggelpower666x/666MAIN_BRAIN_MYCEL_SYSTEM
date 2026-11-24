# CODING PROFI — GitHub-Quellspiegel

Stand: 2026-11-25 (LIVE BACKUP R01)

## Verifizierter Plugin-Current zum Import

- Plugin: `sceeri-intelligence` / **L.Y.V.R.A. CODING PROFI**
- Plugin-ID: `plugins_6af753996b5c81918daadc40df266ce7`
- Produktive Plugin-Version beim letzten Live-Backup-Readback: **0.87.8**
- Produktive Release-ID: `pluginrel_6b061b356f988191aa4728df7df7af76`
- Quelldateien im Verzeichnis `plugin_source/`: **268**
- Die Originalpfade innerhalb des Plugins werden relativ zu `plugin_source/` erhalten.

## Zuständigkeit / Integrationsgrenze

Dieser GitHub-Ordner ist ein **bearbeitbarer Quellspiegel** des angegebenen Plugin-Releases, keine zweite Runtime, kein automatischer Plugin-Update-Mechanismus und kein Current-Pointer für andere Systeme. Der installierte Plugin-Release bleibt maßgeblich für das tatsächliche ChatGPT-Plugin. Für spätere Änderungen: Plugin-Current lesen, Änderungen minimieren, Backup und negative Gegenproben, guarded Plugin-Publish, Readback; dann diesen GitHub-Quellspiegel mit neuer Release-ID synchronisieren.

## Historische Auftragssteuerung 0.87.7 (weiterhin vorhanden)

- `plugin_source/skills/sceeri-coding-profi-chat/SKILL.md`: Verbindliche Auftragssteuerung
- `plugin_source/references/chat-betriebsmodell.md`: Auftragspriorität, begrenzte Blocker und Wiederverwendung gültiger Tests
- `plugin_source/references/coding-profi-development.md`: gezielte Wiederaufnahme und Projektkontinuität
- `plugin_source/plugin.json` und `plugin_source/.codex-plugin/plugin.json`: übereinstimmende Plugin-Version 0.87.7

## Quelle, Sicherung und Gültigkeit

Diese Quellen wurden aus dem installierten Plugin per autorisiertem Readback als UTF-8-Text abgerufen. Bei Text-API-Reads können ursprüngliche Zeilenenden normalisiert werden; dieser Spiegel garantiert keine byteidentische Rekonstruktion eines möglicherweise binär verpackten Server-Archivs. Er bietet die vollständigen textlesbaren Inhalte aller 268 Dateien und ihre relativen Pfade. Die vorherige Projektbasis mit `README.md`, `ARCHITECTURE.md`, `OPEN_WORK.md`, sowie den Evidenzen R05 und R06 wurde aus dem bestehenden CODING-PROFI-Git-Stand erhalten und hier additiv aufgenommen.

Die letzte Änderung R01 betrifft nur `PROJECTS/LYVRA_CODING_PROFI/`. Andere `PROJECTS`-Zuständigkeiten bleiben unangetastet. Die ursprünglichen Plugin-Releases bleiben unabhängig von diesem Quellspiegel verfügbar.


## Live-Backup-Synchronisation R01 (2026-11-25)

Autorität: **ausschließlich das installierte CODING-PROFI-Plugin** `plugins_6af753996b5c81918daadc40df266ce7`.
Verifizierter Plugin-Release: **0.87.8** / `pluginrel_6b061b356f988191aa4728df7df7af76`.
Mirror: `PROJECTS/LYVRA_CODING_PROFI/plugin_source/` mit normal lesbaren Quelldateien; **kein ZIP-Backup**.
Nach diesem Release synchronisierte Dateien:
- `skills/sceeri-coding-profi-chat/SKILL.md`
- `references/coding-profi-development.md`
- `references/coding-profi-live-backup.md`
- `plugin.json`
- `.codex-plugin/plugin.json`

Verbindlicher Ablauf: Original-Plugin ändern → Release und Dateien zurücklesen → GitHub-Backup im selben autorisierten Update nachführen und Commit/Dateien zurücklesen. Dies ist kein autonomer Dauerprozess und ändert weder die native Identität noch die eigentliche Plugin-Laufzeit. Bei fehlgeschlagenem Repo-Abgleich **BACKUP_SYNC_PENDING**, nicht stille Behauptung eines aktuellen Backups. Der Vollbestand der übrigen Plugin-Quelldateien bleibt im selben Ordner erhalten. Das Backup darf das Original nicht automatisch zurücküberschreiben.
Quelle: `plugin_source/references/coding-profi-live-backup.md`.
Recovery vor der Synchronisation: `backup/coding-profi-pre-live-backup-r01-20261125` bei `9f145d2e9ef30a2678c63b38a2b16dd69f72a55e`.
