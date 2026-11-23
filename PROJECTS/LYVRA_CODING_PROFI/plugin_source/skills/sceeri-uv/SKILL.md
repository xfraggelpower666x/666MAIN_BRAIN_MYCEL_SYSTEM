---
name: sceeri-uv
description: "Unterstützt uv bei Python-Versionen, Abhängigkeiten, Lockfile, Synchronisierung, Ausführung und kontrollierter Migration."
---


# uv-Projektworkflow

Ermittle zuerst, ob das Zielprojekt uv verwendet und in welchem Workspace oder Paket die Änderung liegt. Prüfe Projektdatei, Lockfile, Python-Pin, Gruppen, Extras und CI. Ordne die Aufgabe der passenden uv-Funktion zu: Abhängigkeit hinzufügen oder entfernen, sperren, synchronisieren, Projektkommando im verwalteten Environment starten oder ein isoliertes Werkzeug ausführen.

Behalte das gewählte Abhängigkeitsverfahren bei. Eine Migration von Pip, Poetry oder einem anderen Manager ist ein eigener Auftrag mit Vergleich direkter und transitiver Abhängigkeiten, Indizes, Python-Versionen und CI-Einstieg. Prüfe bei Releases, dass der Lockstand zur Projektdatei passt und die Umgebung reproduzierbar ist. Weise Befehle als Anleitung oder als tatsächlich ausgeführt aus.
