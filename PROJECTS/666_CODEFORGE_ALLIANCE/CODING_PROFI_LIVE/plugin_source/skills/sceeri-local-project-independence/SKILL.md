---
name: sceeri-local-project-independence
description: Develop and verify independently runnable local project code while the coding plugin operates as a separate process.
---

# Eigenständiges Zielprojekt

Halte Plugin, Basis und Kandidat in getrennten Verzeichnissen. Das Zielprojekt behält seine normalen Imports, Startbefehle, Laufzeitabhängigkeiten und Tests. Generierter Zielcode benötigt weder den Coding-Agent-Prozess noch dessen Pakete, Tokens, native Systeme oder Arbeitsverzeichnis.

Vergleiche Basis und Kandidat mit demselben Regressionstest in zwei getrennten freigegebenen Projektkopien, sofern eine echte Host-Umgebung vorhanden ist. Prüfe jeweils den normalen Projekteinstieg. Gib sonst Eingabe, Soll-Ausgabe und einen kopierbaren Testplan an. Der Chat-Review belegt die Inspektion der sichtbaren Dateien.

Fasse Testzustände getrennt zusammen. Ein fehlender Import oder gesperrter Start ist ein eigener Befund. Bei Projekten mit Framework-Abhängigkeiten oder Assets prüfe die volle eigenständige Projektumgebung. Das Vergleichswerkzeug übernimmt nur den dokumentierten Python-Quellumfang des bestehenden Prüfpfads.
