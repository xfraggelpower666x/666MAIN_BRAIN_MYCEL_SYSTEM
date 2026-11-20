# 666TDH · GitHub-Current-Check und vollständige Git-Arbeitsbaum-Sicherung

- Systemstart: `python tdh.py 666TDH SYSTEMSTART`
- Native Python-Regressionssuite: `python -m unittest discover -s tests -v`
- Current, alle Hashes, fünf Childs und neun read-only Daemon-Routen prüfen:
  `python tools/verify_and_backup.py`
- Vollständigen **getrackten Repo-Baum** als offline wiederherstellbares ZIP
  aus einem sauberen lokalen Git-Checkout sichern:
  `python tools/verify_and_backup.py --backup-dir <VERZEICHNIS_AUSSERHALB_DES_REPOS>`
- Auf Windows: `STARTEN.bat` verwenden (Doppelklick, Python 3.10+ und Git).

Der Backup-Lauf nimmt exakt `PROJECTS/666TDH` aus dem geprüften Git-HEAD auf,
inklusive aller getrackten Binärdateien und unveränderten Childs. `git archive`,
`git ls-tree`, ZIP-CRC, jede einzelne ZIP-Datei-SHA-256 und die Gesamt-ZIP-SHA-256
werden verglichen. Das JSON-Manifest wird neben dem ZIP ausgegeben. Das Skript
überschreibt keine existierende Sicherung und schreibt nicht in das Repo.

**Wichtige Grenze:** Das externe FSE-Original unter `SOURCE_VAULT_ONLY` ist nicht
im öffentlichen Git-Repo enthalten und daher auch nicht im ZIP. Der Quellprovider
ist gesondert mit seinen Recovery-Rechten zu sichern. Vor der Rücksicherung
prüfen, dass Git-HEAD, Current und Backup-Manifest dieselbe Revision meinen.
Keine automatische Recovery-Veröffentlichung, keine PFS-Mutation.

Interaktive ChatGPT-Host-Abnahme ist ein gesonderter, evidenzpflichtiger Schritt.
Ein lokaler Chromium-Renderer-Test bestätigt keine ChatGPT-Host-Integration.
