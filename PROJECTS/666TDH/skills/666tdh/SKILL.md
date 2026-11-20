---
name: 666tdh
description: Rehydriert 666TDH aus seinem nativen Repo-Current und bindet nur direkt ausgewählte Childs.
---

Lies im produktiven Branch 666MAIN_BRAIN unter PROJECTS/666TDH zuerst CURRENT_POINTER.json am aufgelösten Commit. Nutze ausschließlich die referenzierten Dateien desselben Commits. Im lokalen Checkout liefert python tdh.py 666TDH SYSTEMSTART --bootstrap das geprüfte Startpaket. Für einen Child ergänze den verifizierten Registry-Token vor SYSTEMSTART.

SYSTEMSTART am Hub zeigt das Branch-Menü. STATUS zeigt den verifizierten Stand. WEITER und NEW CHAT lesen den zielgebundenen Handoff aus demselben Current. FSE und SHACHIVITI behalten ihre dokumentierten Holds zur nativen Quellidentität.

Wenn ein erforderliches Objekt fehlt, melde READBACK_PENDING oder HOLD mit Objekt und Revision. Zeichne den sichtbaren Current und die Host-Abnahme getrennt aus. Ein PFS-Backup, ein historischer Drive-Pointer oder ein fremder Handoff liefert keine Ausführungsautorität.

For `666TDH UPDATE`, also verify and follow
`runtime/REPO_UPDATE_AUTHORITY.md` from the SAME repository Current.
Historical provider-era dual-publish rules under `runtime/hub/` are
source evidence, not permission to mutate PFS or Drive. Preserve the exact
outgoing Git commit as a pre-change recovery ref. Publish staged data first
and CURRENT_POINTER.json as the final commit with checked-ref readback.
Do not report host rendering, PFS refresh or source vault recovery as
complete without direct evidence.

## Additive R3 UI / Daemon / Recovery

Nach verifiziertem Current die vorhandenen R2-Subfacetten (`runtime/facets`)
und die aktuelle R3-UI (`runtime/ui`) verwenden. Der aktuelle Native-Renderer
liefert echte klickbare, evidenzgebundene Inhaltsansichten; auf dem PC erzeugt
`python tdh.py 666TDH DASHBOARD --html ../tdh-hub.html` eine Offline-Datei.
Nur direkt registrierte Menübefehl-Strings dürfen kopiert werden; keine
implizite Ausführung, keine fremden Trigger und keine automatischen Writes.

Ein einziger beratender Daemon wird zielgebunden gerendert. Die bislang
historisch dokumentierten `666TDH DAEMON ...`-Befehle laufen ausschließlich
über den Root-Parser und die `daemon`-Registry in `runtime/TRIGGERS.json`.
`runtime/hub/daemon/DAEMON_ROOT_ROUTES.md` ist der Repo-Adapter-Vertrag.
Daemon: `ROUTING_AUTHORITY=NONE`, `WRITE_AUTHORITY=NONE`.
Ein Daemon-STOP ist lediglich für die jeweilige lokale Anzeige gültig.

Für echte vollständige Offline-Sicherungen siehe `tools/README.md` und
`STARTEN.bat`. Der Git-Recovery-Branch bleibt die vorangestellte vollständige
Repo-Pre-Change-Sicherung. FSE-Vault-Originale bleiben extern und dürfen nicht
öffentlich eingebunden werden. Lokale Chromium- und Python-Tests ersetzen
keinen tatsächlichen ChatGPT-Host-Test. Erfolgsgates getrennt ausweisen.
