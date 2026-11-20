# Engine Specifications — LYVRA DOLMETSCHER v1.2.3

## E01 — Bootstrap Gate

Akzeptiert ausschließlich einen exakten Textalias oder ein reales, lesbares und verifizierbares Paketereignis. Dokumentierte Trigger bleiben inert.

## E02 — Language Resolution

Ermittelt getrennt `source_language`, `target_profile` und `system_language`. Direktrouten haben Vorrang; Pivot-Routing ist nicht erforderlich.

## E03 — HOLD Engine

`MICRO_HOLD` verarbeitet einzelne Eingaben ohne Fertig-Gate. `BATCH_HOLD` sammelt FIFO bis zum exakten Abschlussbefehl `fertig`. Rohtexte sind unveränderlich und dürfen nicht überschrieben werden.

## E04 — Interpretation Pipeline

Die Pipeline kombiniert Kontext, Beziehung, Emotion, Kultur, Register und Zielprofil. Keine Einzelrolle darf den Quellinhalt besitzen oder eigenmächtig erweitern.

## E05 — Emoji Engine

Emojis werden nach Bedeutungs-, Emotions-, Beziehungs-, Absichts- und Tonkausalität ergänzt. Wörterersatz, Informationserfindung und Konflikt mit dem Quelltext sind verboten.

## E06 — Quality Engine

Prüft mindestens Inhaltstreue, Negationen, Zahlen, Namen, Sprecher, Register, Format und Emoji-Drift. Kritische oder mehrdeutige Ausgaben werden rücksemantisch geprüft.

## E07 — Repair Engine

Erlaubt maximal drei minimalinvasive Durchläufe. Jeder Durchlauf benötigt Re-Audit; bei Fehlschlag wird zurückgerollt oder blockiert.

## E08 — Lifecycle Engine

Freeze nur nach Audit-PASS. Das Manifest bindet alle freigegebenen Dateien per SHA-256. ZIP-Erstellung benötigt CRC-Test und vollständigen Readback.

## E09 — Recovery Engine

Restore verifiziert Identität, Namespace, Version, Manifest, CRC, Checkpoint und Konfliktlage. Ein älterer Zustand darf keinen neueren verifizierten Zustand überschreiben.

## E10 — Isolation

Keine Engine-Funktion darf einen zentralen LYVRA-Integrationsrouter, einen zweiten Bootstrap, einen zweiten Updateweg, LYVRA-Core-, 666PFS- oder Drive-Mutation erzeugen.

## Stage-02-Entscheidung

Die aus dem Handoff genannten Punkte `SRS`, `SAS`, `Engine Specs`, `Requirement IDs` und `Master Audit` werden als Dokumentationsschicht integriert. Es wurden keine neuen Laufzeitfunktionen erfunden.
