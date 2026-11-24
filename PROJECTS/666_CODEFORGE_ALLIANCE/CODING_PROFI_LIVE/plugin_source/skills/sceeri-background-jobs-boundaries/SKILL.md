---
name: sceeri-background-jobs-boundaries
description: "Prüft FastAPI-Hintergrundaufgaben, Queue-Grenzen, Transaktionen und zuverlässige Zustellung."
---


# Hintergrundaufgaben

1. Klassifiziere Dauer, Fehlerfolgen, Wiederholung und Persistenzbedarf. In-Process-Tasks passen zu kurzen Best-Effort-Aufgaben, deren Verlust akzeptabel ist. Kritische, lange oder wiederholbare Arbeit gehört in eine separat verwaltete Queue oder einen Worker.
2. Persistiere den fachlichen Zustand vor dem Start. Muss fachlicher Commit und Einplanung gemeinsam abgesichert sein, prüfe ein transaktionales Outbox-Muster. Übergib IDs oder kleine validierte Nutzlasten. Der Worker öffnet eigene Ressourcen und erhält eine Korrelations-ID.
3. Plane Idempotenz anhand einer Ereignis- oder Auftrags-ID, begrenzte Retries und Sichtbarkeit endgültiger Fehler. Kläre Verhalten bei Prozessabbruch, doppelter Zustellung und fehlenden Ressourcen.
4. Gib die Entscheidung mit Zustellanforderung, Transaktionsgrenze und Tests für Fehler, Wiederholung und Wiederanlauf aus. Ein In-Process-Task liefert keine dauerhafte Zustellgarantie.
