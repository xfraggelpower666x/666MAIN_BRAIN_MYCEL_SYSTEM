---
name: sceeri-pytest-service
description: "Plant oder prüft deterministische pytest-Tests, Fixtures, FastAPI-Overrides und HTTP-Transport-Mocks."
---


# pytest für Services

1. Prüfe Testlayout, Datenbankstrategie und vorhandene Fixtures. Verwende kleine deterministische Fabriken mit expliziten Overrides. Halte veränderlichen Zustand pro Test isoliert. Nutze geteilten Scope nur für Ressourcen mit definiertem Reset.
2. Ersetze Abhängigkeiten an ihrer Vertragsgrenze. Entferne FastAPI-Overrides beim Abbau auch bei Fehlern. Prüfe tatsächliche Route und Status, Payload sowie Seiteneffekt, wenn diese zum Vertrag gehören.
3. Simuliere externe HTTP-Anbieter an der Transport- oder Client-Grenze. Halte Uhr, Zufall und Eingabedaten kontrollierbar. Parametrisiere vergleichbare Grenzfälle. Prüfe Fehlerpfade und erwartete Zustandsänderungen explizit.
4. Trenne fokussierten Regressionstest, relevante Suite, Typprüfung und Lint. Berichte pro Lauf Umgebung, Befehl, Ergebnis und offene Prüffälle.
