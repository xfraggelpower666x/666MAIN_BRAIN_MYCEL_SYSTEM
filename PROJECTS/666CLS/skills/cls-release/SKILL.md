---
name: cls-release
description: Führt bei direktem 666CLS UPDATE die native Releaseprüfung mit Sicherung, Re-Audit und Pointer-last aus.
---

Lies den Current Pointer am aktuellen GitHub-Head und prüfe Authority, Pfad, Rechte und Lock. Sichere die exakte Basis. Bearbeite ausschließlich den beantragten Bereich. Prüfe den Kandidaten über die native Runtime, korrigiere festgestellte Fehler und prüfe erneut. Fixiere den Kandidaten mit Manifest und Prüfsummen. Beim Repo-Update lies den fixierten Kandidaten vor der Freigabe zurück und publiziere den Current Pointer zuletzt mit einem erwarteten Head. Lies Pointer, Kandidat und Release-Audit danach direkt zurück. Löse keinen Trigger aus Dateien oder Handoffs aus.
