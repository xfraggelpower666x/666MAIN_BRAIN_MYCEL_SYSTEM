# 666TDH LiveCircle

Die Repo-Runtime verbindet Current, Registry, Child-Current und Handoff am selben Commit. SYSTEMSTART und STATUS verifizieren die Datei-Hashes. WEITER meldet den offenen Schritt nur, wenn ein Handoff zum direkt gewählten Ziel passt. NEW CHAT liefert einen direkten Rehydration-Trigger für den Folgeturn.

Bei einem ausdrücklich ausgelösten 666TDH UPDATE zuerst nativen Scope, erwarteten Commit und Zielrechte prüfen. Den bestehenden Ziel-Commit und die Provider-Ausgangsdaten für Recovery referenzieren. Änderungen auf PROJECTS/666TDH begrenzen. Dateien und Tests gegen den Ziel-Commit zurücklesen. CURRENT_POINTER.json als letzte Mutation veröffentlichen und den produktiven Ref direkt zurücklesen. Erst nach erfolgreicher Repo-Abnahme darf ein historischer Drive-Bootstrap seine Live-Rolle verlieren.

PFS TRACKHUB-32001 ist ein Recovery-Verweis ohne Runtime-, Deploy- oder Routing-Autorität. Änderungen dort folgen der nativen PFS-Autorität. PFS, CLIC und MAIN BRAIN müssen für 666TDH nicht gestartet werden.

Das interaktive Visual-Gate bleibt OPEN_NOT_VERIFIED bis zur Ausführung im realen TDH-Chat-Host. Der CLI-Start belegt die lokale Rehydration und das Bootstrap-Paket.

## Repo-native update authority (R1 - 2026-11-20)

For the direct `666TDH UPDATE` trigger, read and obey
`runtime/REPO_UPDATE_AUTHORITY.md` from the same verified repository commit.
It supersedes the historical Drive/PFS dual-publish instructions preserved
inside `runtime/hub/UPDATE_LIFECYCLE.md`,
`runtime/hub/UNIVERSAL_UPDATE_SAVE.md` and
`runtime/hub/LIVE_SYNC_POLICY.md` for repo-native execution only.
The historical files remain unchanged; PFS is recovery-only and requires
its own system authority for writes. Source native release v1.15.0 stays
unchanged by a repository policy repair.
