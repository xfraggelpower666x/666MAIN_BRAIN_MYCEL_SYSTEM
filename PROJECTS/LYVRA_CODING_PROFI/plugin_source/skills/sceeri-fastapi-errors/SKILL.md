---
name: sceeri-fastapi-errors
description: "Gestaltet konsistente FastAPI-Fehlerverträge mit Domain-Exceptions, Validierung, Auth und sicherer Fehlerausgabe."
---


# FastAPI-Fehlerverträge

1. Erfasse bestehende Statuscodes, Antwortformate, Fehlercodes und Client-Verträge. Trenne Domainfehler, Request-Validierung, Framework-HTTP-Fehler, Authentifizierung und unerwartete Ausnahmen.
2. Halte fachliche Fehler unabhängig von HTTP. Übersetze sie am API-Rand in stabile Fehlercodes, passende Statuscodes und eine sichere Antwort. Bewahre relevante Framework-Header wie Authentifizierungs-Challenges. Einheitliche Fehlerhüllen müssen vorhandene Verbraucher berücksichtigen.
3. Behalte Validierungsdetails gezielt bei, soweit sie für Clients nötig und frei von sensiblen Daten sind. Gib bei unerwarteten Fehlern einen generischen 500-Text mit Korrelations-ID aus und protokolliere die Ursache einmal an der passenden Grenze.
4. Prüfe repräsentative 4xx, Validierung, fehlende Anmeldung, fehlende Rechte und unerwartete Fehler. Belege Antwortform, Status und Header über die tatsächliche Route.
