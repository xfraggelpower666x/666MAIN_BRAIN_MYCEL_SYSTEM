# RADIO WAVE v6.66 · MilkDrop-Import R17

Basis: `bc29ee8eb14635cd913715bc5bf544b0a8be3ee2`

Der ZIP-Import entfernte die bestehende persönliche Bibliothek vor dem Umbenennen des Staging-Ordners. Ein lokal reproduzierter Umbenennungsfehler machte die alten Presets danach unlesbar. Der Patch verschiebt die vorhandene Bibliothek vorübergehend in ein separates Backup. Bei Fehlern beim Umbenennen oder beim Schreiben des Manifests wird sie zurückgestellt. Falls das Zurückstellen scheitert, bleibt das Backup erhalten und der Fehler nennt den Recovery-Pfad. Nach erfolgreichem Schreiben des Manifests wird das Backup bereinigt.

| Prüfung | Ergebnis |
|---|---|
| Node-Syntaxprüfung für `main.js` | PASS |
| `node --test tests/personal-milkdrop-archive.test.cjs` | 6/6 PASS. Zwei bestehende Fälle und vier neue Regressionen für Übernahmefehler, Manifestfehler, fehlgeschlagenes Rollback und erfolgreiche Übernahme. |
| SHA-256 für `main.js` | Eintrag aktualisiert und lokal bestätigt. |

Die Tests verwenden temporäre reale Verzeichnisse und Test-Doubles für PowerShell sowie gezielt ausgelöste Dateisystemfehler. Windows-/Electron-Laufzeit, Installer und tatsächliche ZIP-Extraktion unter Windows bleiben offen. Fresh-Chat- und Provider-Abnahmen von MAIN BRAIN behalten ihren eigenen Status.
