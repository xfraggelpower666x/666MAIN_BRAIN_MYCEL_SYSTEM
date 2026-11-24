# CODING PROFI — dreistufiger Live-Backup-Vertrag

Status: VERBINDLICHER CODING-PROFI-WORKFLOW
Owner/Authority: L.Y.V.R.A. CODING PROFI, installiertes Plugin
Plugin-ID: `plugins_6af753996b5c81918daadc40df266ce7`
Backup-Ziel: `xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM`, Branch `666MAIN_BRAIN`,
`PROJECTS/LYVRA_CODING_PROFI/plugin_source/`

## Grundsatz

**Eine Autorität, zwei getrennte Auslieferungs-/Aufbewahrungsoberflächen.**
Das installierte CODING-PROFI-Plugin bleibt Original, fachliche Autorität, eigentlicher
Ausführungsort und einziger maßgeblicher Release-Current. Der zusätzliche GitHub-Pfad
ist ein *editierbarer, entpackter, versionsgebundener Live-Backup-Spiegel*, nicht
ein zweites Plugin, keine neue Runtime, kein zweiter Current-Pointer, kein Ersatz-Host
und keine fremde native Authority. `LYVRA`, `666DEV`, `666CLIC` und `666MAIN BRAIN`
behalten ihren eigenen Current; der Shared-Repo-Branch begründet keine Authority.

## Drei Schritte bei JEDER autorisierten Änderung des CODING-PROFI-Plugins

1. **Original/Änderung:** Den tatsächlichen Plugin-Current, Release-ID, betroffene
   Dateien und Auftrag prüfen; bestehende Struktur erhalten, minimalinvasiv bearbeiten,
   unveränderte Checks wiederverwenden; relevante neue Tests ausführen. Vor relevanten
   Mutationen Wiederherstellungsstand sichern.
2. **Plugin-Publikation:** Ausschließlich unter derselben Plugin-ID mit
   `expected_release_id` veröffentlichen. Unveränderte Assets, Logos, Skills,
   Host-Bindings und übrige Dateien nicht ersetzen. Unmittelbar Plugin-Metadaten
   und betroffene Dateien zurücklesen und tatsächliche neue Version/Release-ID
   feststellen. Ist dieser Schritt nicht verifiziert, niemals das Backup als
   produktiven Stand deklarieren.
3. **GitHub-Live-Backup:** Aus dem *tatsächlich verifizierten neuen Plugin-Release*
   die betroffenen Dateien unter ihren relativen Originalpfaden in
   `PROJECTS/LYVRA_CODING_PROFI/plugin_source/` mit gültigem GitHub-HEAD,
   expected Blob SHA und nicht-erzwingendem Commit synchronisieren.
   Gelöschte Originaldateien dürfen nur nach explizit bestätigter, auf Original
   belegter Löschung entfernt werden. `SOURCE_CURRENT.md` mit genau der neuen
   Plugin-ID, Version, Release-ID, Scope und Backup-Commit aktualisieren.
   Commit/Dateiinhalte und Branch-HEAD unmittelbar zurücklesen. Erst dann
   `PLUGIN_CURRENT_VERIFIED + LIVE_BACKUP_SYNC_VERIFIED` melden.

**Fortlaufend** heißt *bei jeder neuen tatsächlich beauftragten und ausgeführten
Plugin-Änderung im selben Update-Vorgang nachlaufen*; es behauptet keinen unsichtbar
laufenden Hintergrunddienst oder autonomen Trigger. Ohne erreichbaren Plugin- oder
GitHub-Connector darf nicht so getan werden, als sei synchronisiert worden.
Das gesamte Backup bleibt als einzelne les- und editierbare Dateien, **nicht als ZIP**.

## Fehlersicherheit

- Wenn Schritt 2 fehlschlägt: `PLUGIN_WRITE_BLOCKED`; keinen produktiven Versionssprung
  behaupten und kein Kandidat/Backup zur Original-Autorität machen.
- Wenn Schritt 2 erfolgreich, aber Schritt 3 scheitert: Plugin-Current bleibt gültig,
  Status **`BACKUP_SYNC_PENDING`**, mit exakt nicht gesichertem Release und Dateipfad.
  Nicht zurückrollen oder auf alte Plugin-Version zurücksetzen. Beim nächsten
  Zugriff erst den Rückstand nach verifiziertem Plugin-Current abgleichen.
- GitHub-HEAD, Scope oder erwarteter Datei-SHA abweichend: `CONFLICT_QUARANTINE`,
  neu prüfen; kein Force-Push, blindes Überschreiben oder Löschen.
- Backup-Dateien sind *recoveryfähige Quellen*, aber ihre Rückübernahme ins Plugin
  erfordert eine eigene autorisierte Entscheidung mit Vergleich gegen den aktuellen
  installierten Plugin-Release, Test und geschützter Publikation.
- Keine Secrets, Zugangstokens, private Logs oder Nutzerkonversationen im Repo-Backup.
  Nur freigegebene Plugin-Quelldateien und sachliche Status-/Hash-Evidenz.
- Änderungen an eigenständigen Zielprojekten folgen deren jeweiligen nativen Repos;
  nicht ungefragt in dieses CODING-PROFI-Plugin-Backup spiegeln.

## Abnahmestatus

`PLUGIN_AUTHORITY` ist erst nach dem installierten Release-Readback `VERIFIZIERT`.
`LIVE_BACKUP` ist erst nach dem GitHub-Readback derselben Release-ID `VERIFIZIERT`.
`ZIP_DELIVERY` ist nicht Teil des Backup-Ablaufs.
