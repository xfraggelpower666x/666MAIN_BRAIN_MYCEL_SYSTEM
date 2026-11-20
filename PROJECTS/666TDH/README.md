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
