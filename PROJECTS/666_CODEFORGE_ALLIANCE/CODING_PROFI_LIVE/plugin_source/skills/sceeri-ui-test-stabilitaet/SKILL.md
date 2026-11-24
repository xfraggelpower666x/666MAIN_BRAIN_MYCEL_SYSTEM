---
name: sceeri-ui-test-stabilitaet
description: "Plant oder repariert Browser-, Komponenten- und Terminaltests mit isolierten Fixtures und beobachtbaren Bereitschaftssignalen."
---

# Stabile UI-Tests

- **Browser/E2E**. Prüfe kritische Nutzerwege über zugängliche Locator-Rollen und beobachtbare UI-Zustände. Isoliere Speicher, Kontext, Projekte und Mocks. Prüfe Service Worker, Caching und Navigation entsprechend dem Testziel.
- **Komponenten**. Prüfe Fixture, Mount, Mock-Verträge und Reaktion auf Eingabe. Warte auf belegte Bereitschaft. Isoliere beim Debugging kalte Starts, Neu-Bundling, Layout, Touch und Fokus.
- **TUI**. Prüfe Tastatur, Maus, Größenwechsel und Ausgabe in einer definierten Terminalgröße. Verwende kontrollierte Uhren und warte auf die erwartete Ansicht oder einen Frame mit begrenzter Frist.
- **Flakes**. Lies CI-Artefakte, Plattform und ersten Fehlversuch. Vergleiche Einzeltest und Suite. Kontrolliere globale Zustände, Dateipfade, Timer und Prozessbereinigung. Behandle erfolgreiche Retries als Diagnosehinweis. Stelle Geschwindigkeitsbehauptungen nur auf wiederholte Messung.

## Visuelle Regression

Nutze [UI-Varianten und Asset-Abnahme](../../references/ui-varianten-und-asset-abnahme.md), wenn Aussehen, Branding, Statusrollen oder mehrere Viewports betroffen sind. Halte Rendering und den tatsächlich ausgelösten Nutzerfluss als eigene Prüfungen fest.
