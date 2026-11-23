---
name: sceeri-dockerize-service
description: "Plant oder prüft Dockerfiles und lokale Compose-Setups für Python-Dienste mit reproduzierbarem Build und Healthchecks."
---


# Python-Dienst containerisieren

1. Prüfe vorhandene Containerdateien, Lockfile, Python-Version, Einstieg, Port, Health-Route und benötigte Dienste. Verwende echte Projektsignale für Datenbank, Redis und weitere Abhängigkeiten.
2. Entwirf einen reproduzierbaren Build mit passender Basisversion, separater Build-/Laufzeitphase bei Bedarf, kleinem Kontext und Nicht-Root-Benutzer. Verwende vorhandenes Lockfile und Abhängigkeitswerkzeug. Ignoriere lokale Umgebungen, Caches und Geheimnisse im Build-Kontext.
3. Stelle Compose bei Bedarf als lokale Entwicklungsumgebung bereit. Lege Konfigurationsvorlage mit Platzhaltern, Abhängigkeiten, persistente Volumes und einen erreichbaren Healthcheck fest. Unterscheide Startreihenfolge von tatsächlicher Bereitschaft. Bind Mounts gehören in ein bewusstes Entwicklungsprofil.
4. Liefere auf Auftrag Dateien für das Zielprojekt und den Prüfpfad für Build, Start, Health, Logs und Stopp. Führe Tests nur bei verfügbarem und autorisiertem Docker aus. Berichte Ziel und Ergebnis eines Deployments ausschließlich aus beobachteten Daten.
