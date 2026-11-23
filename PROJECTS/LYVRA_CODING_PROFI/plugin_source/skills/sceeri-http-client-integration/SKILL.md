---
name: sceeri-http-client-integration
description: "Entwirft ausgehende HTTP-Integrationen mit Client-Lebenszyklus, Timeouts, Retries und Response-Verträgen."
---


# Ausgehende HTTP-Integration

1. Prüfe den vorhandenen Client, Startup und Shutdown, Konfiguration, Auth und Fehlerübersetzung. Verwende für asynchrone Dienste einen passenden wiederverwendbaren Async-Client. Der Dienst besitzt seinen Lebenszyklus und schließt Ressourcen am Ende.
2. Kapsle Basis-URL, Auth, Header und Timeout zentral. Vendor-spezifische Module besitzen Endpunkte und Payloads. Validiere externe Antworten an der Grenze, bevor sie in Fachlogik gelangen.
3. Begrenze Zeit und Wiederholungen. Wiederhole nur bewusst ausgewählte transiente Fehler bei idempotenten Aktionen oder explizit abgesicherter Wiederholung. Respektiere bei 429 einen passenden Retry-After-Wert. Parse- und Vertragsfehler werden als solche gemeldet.
4. Propagiere erlaubte Korrelationsdaten. Verwende Transport-Mocks für Timeout, Retry und Nicht-Retry, Statusmapping, ungültige Antworten und Client-Schließung. Führe Unit-Tests ohne Anbieterzugriff aus.
