# Migration des produktiven 666TDH-Stands v1.15.0

Quellautorität ist der native 666TDH-Live-Pointer vom 29.10.2026 mit den verknüpften Hub-, Child-, Visual-, Daemon- und Handoff-Objekten. Die Reconciliation für CLIC-Delivery ist im gelesenen Stand enthalten. Für den Zielkandidaten bleibt die Release-Identität v1.15.0 erhalten.

Der neue Repo-Pointer bindet den Repo-Launcher, den LiveCircle, die Registry, den Triggervertrag, den Handoff und die entpackten Laufzeitdateien über SHA-256. Der bisherige Drive-Pointer und der Handoff bleiben unverändert als Provenienz erhalten. Die Rollen der paketinternen Alt-Pointer und Triggertexte sind auf Quellmaterial beschränkt. Die gültigen Repo-Routen stehen in runtime/TRIGGERS.json.

SOURCE_OBJECTS.json erfasst die 23 Objekte der Live-Quelle und fünf SHACHIVITI-Originale. SOURCE_FILES.json ordnet entpackte Pfade, Varianten, SHA-256 und Größen ihren Provider-Objekten zu. Identische FULL- und PORTABLE-Dateien haben dieselbe Zielreferenz. Abweichende PORTABLE-Dateien verbleiben als Provenienz. Eingebettete Archivoriginale liegen außerhalb des Runtime-Baums, soweit die Datenprüfung sie freigab.

Das FSE-Originalarchiv unter SOURCE_VAULT enthält potenzielle Zugangsdaten in verschachteltem Material. Es verbleibt als Original am Quellprovider. SOURCE_VAULT_ONLY.json enthält den Recovery-Verweis mit Originalpfad und Prüfsumme. Die 21 FSE-Steuer- und Quelldateien des Live-Pakets sind entpackt im Projekt vorhanden. Die bekannten nativen Identitäts-Holds von FSE und SHACHIVITI bleiben offen.

Frühere Provider-History- und Backup-Ordner bleiben außerhalb der laufenden Projektdaten. Sie wurden durch die Migration nicht verändert. Unabhängige Chat-Host-Abnahme und der produktive GitHub-Cutover bleiben getrennt prüfbar.
