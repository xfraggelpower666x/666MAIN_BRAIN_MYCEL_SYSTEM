# 666TRACKDESIGNHUB · 666TDH

Eigenständiges Trackdesign-System 666TRACKHUB-001. Der produktive Current wird über PROJECTS/666TDH/CURRENT_POINTER.json im Branch 666MAIN_BRAIN aufgelöst. Die Migration übernimmt den nativ gelesenen Release v1.15.0. Der Branch enthält ein ausführbares Projekt mit entpackten Hub-, Child-, Daemon- und Visual-Dateien.

```text
python tdh.py 666TDH SYSTEMSTART
python tdh.py 666TDH TD SYSTEMSTART --bootstrap
python tdh.py 666TDH LCTS WEITER
python tdh.py 666TDH DTSTE NEW CHAT
python -m unittest discover -s tests
```

Der Einstieg benötigt Python 3.10+. Der Bootstrap enthält die verifizierten Laufzeitdokumente für den Chat-Host. Die Musik-Workflows behalten ihre nativen Output-Verträge. Ein Chat-Host verarbeitet die Eingabe und erzeugt die Track-Ausgabe. Chat-Anbindung und frische Host-Abnahme sind eigene Prüfschritte.

TD, LCTS, DTSTE, FSE und SHACHIVITI bleiben eigenständige Childs von 666TDH. Der produktive PFS-Child-Eintrag TRACKHUB-32001 hatte bereits Recovery-only-Status. Der Repo-Current bindet keine Datei aus PFS oder MAIN BRAIN ein. Die fünf Branch-Stände sind in runtime/REGISTRY.json mit eigenen Current-Pfaden registriert.

- [Rehydration](runtime/REHYDRATION.md)
- [LiveCircle und Update](runtime/LIVECIRCLE.md)
- [Chat-Host-Bindung](skills/666tdh/SKILL.md)
- [Migration und Datenprovenienz](provenance/MIGRATION.md)

## Repo-native update authority

The standalone repository update contract is
[runtime/REPO_UPDATE_AUTHORITY.md](runtime/REPO_UPDATE_AUTHORITY.md).
The historical Drive/PFS dual-publish policies in the extracted Hub
are retained as evidence; they cannot authorize PFS or Drive mutation.
`666TDH UPDATE` changes only this project's repository tree, with
pre-change recovery, verified data, and CURRENT_POINTER.json last.
The native provider source release is still v1.15.0; repo policy revision R1
does not relabel child data versions.

The original FSE source-vault archive is not published here because it may
contain credentials. See provenance/SOURCE_VAULT_ONLY.json for safe recovery
metadata. The interactive ChatGPT host acceptance remains open.

## R3 · Intelligent UI, Daemon und Sicherung (additiv)

Der native R2-Subfacetten-Vertrag bleibt erhalten. R3 ergänzt echte lokale
Inhaltsansichten für Hub/Child, ein nachweisbasiertes Menü und die früher
bereits dokumentierten Daemon-Befehle über **denselben** Root-Parser:

```text
python tdh.py 666TDH DAEMON STATUS
python tdh.py 666TDH DAEMON NEXT
python tdh.py 666TDH DAEMON MENU
python tdh.py 666TDH TD DASHBOARD --html ../tdh-td.html
python -m unittest discover -s tests -v
```

Die neun Daemon-Befehle bleiben ausschließlich read-only und ohne eigene
Authority. `DAEMON STOP` betrifft nur die aktuelle Ausgabe, nicht einen
persistenten Hintergrunddienst. Eine lokale HTML-Ansicht aktiviert keinen
Chat-Systemtrigger und schreibt nicht ins Repository.

Für Windows ist `STARTEN.bat` das interaktive Prüf- und Backup-Menü. Ein
vollständiges, restorable Repo-Systembackup aus **allen getrackten TDH-Dateien**
inklusive Binärdateien erzeugt der Nutzer im geklonten Git-Checkout über
`tools/verify_and_backup.py --backup-dir <PFAD_AUSSERHALB_DES_REPOS>`.
Das externe FSE-Original ist ausdrücklich nicht Bestandteil des öffentlichen
Git-Repositories. Näheres: [Backup-Anleitung](tools/README.md).

Die Python-Tests sowie die optionale Browser-Gegenprobe (`tests/browser_ui_smoke.py`,
Playwright/Chromium erforderlich) prüfen verschiedene Ebenen. Der echte
interaktive ChatGPT-Host bleibt `OPEN_NOT_VERIFIED` bis zu dessen Abnahme.
