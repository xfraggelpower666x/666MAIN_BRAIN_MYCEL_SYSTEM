# Entscheidungen aus dem Deep Audit v0.72.0

Auditbasis ist der private Release v0.72.0. Beide Eingangsberichte führen dieselben fünf priorisierten Befunde. Die eingefügte Abschrift endet mit einer unvollständigen Zeile zum Semantic Cyber Field. Für diese Zeile gilt der vollständige Bericht. Inventar und projektgebundene Quelldateien dienen als Referenzen und begründen keine zweite Runtime.

Die Zeilen TS-01 und TS-02 betreffen ToolStarter beziehungsweise Windows-Zielprojekte. ARC-01 betrifft Projektimporte und Exporte. LC-01 und UI-01 beschreiben Chat-Verhalten. Für einen UI-Prüffall mit Textpfad gilt der sichtbare Chat-Einstieg.

| Befund | Umsetzung oder nächste Abnahme |
| --- | --- |
| TS-01 | In ToolStarter umgesetzt. Dateinamen und internes Manifest werden weiterverwendet. Externes Veröffentlichungsmanifest bindet die Artefakte. Regression deckt gemeinsamen und einzelnen Build, Legacy-Ausgabe, Sperre und Abbruch ab. |
| TS-02 | [Windows-Abnahme](windows-lieferabnahme.md) konkretisiert. Reale Windows-Zielapplikation und Direct-Start bleiben als Host-Beobachtung offen. |
| LC-01 | [Wiederaufnahme](wiederaufnahme-pruefung.md) um die Host-Probe ergänzt. Der lesende Strukturhelfer bleibt für seinen definierten Zweck geeignet. |
| UI-01 | [Chat-Abnahme](chat-abnahme.md) um zwei unterscheidbare Projektanker ergänzt. Bei tatsächlich vorhandener nativer Schaltfläche beobachte ihren Nutzerturn im Host. |
| ARC-01 | [XcodeGen](../skills/sceeri-swift-engineer/references/xcodegen.md) und [Build Control](build-control.md) unterscheiden aufgelösten Link und Quellwurzel beziehungsweise Kompression und Nutzdaten. Alte Container bleiben Belege. |
