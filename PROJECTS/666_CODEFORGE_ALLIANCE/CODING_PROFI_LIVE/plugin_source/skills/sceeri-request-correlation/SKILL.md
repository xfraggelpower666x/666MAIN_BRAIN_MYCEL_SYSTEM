---
name: sceeri-request-correlation
description: "Prüft Request- und Job-Korrelation über Eingänge, Logs, Async-Kontext und ausgehende Requests."
---


# Request-Korrelation

1. Lege einen kanonischen Header und eine Vertrauensgrenze fest. Validiere Format und Länge eingehender IDs. Erzeuge am Eingang eine ID, wenn sie fehlt oder unbrauchbar ist. Halte eine Korrelations-ID getrennt von einem Autorisierungsnachweis.
2. Binde die ID an den Request-Kontext und setze ihn auch bei Fehlern zurück. Füge die ID an der Logging-Grenze strukturiert ein. Protokolliere Ausnahmen dort, wo sie sinnvoll behandelt werden, und halte Geheimnisse aus Logs.
3. Propagiere sie gezielt an erlaubte Downstream-Dienste und per explizitem Feld an Worker. Lege Verhalten für neue Async-Tasks und Threads fest. Unabhängige Requests dürfen ihren Kontext nicht mischen.
4. Prüfe mit parallelen Requests, Fehlerpfad und Job, dass Logzeilen und Outbound-Header der richtigen ID folgen.
