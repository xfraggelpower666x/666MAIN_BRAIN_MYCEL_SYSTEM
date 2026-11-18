# Quellenbasis und Prüfgrenzen

| Status | Beleg | Auswirkung |
| --- | --- | --- |
| VERIFIZIERT | Lokale SHA-256 der beiden Original-ZIPs entsprechen dem Reparaturbericht und den archivbezogenen Hashfeldern im bereitgestellten Kandidaten-Pointer. Beide ZIP-Inventare bestehen die enthaltene SHA-256-Prüfung. | Nachvollziehbarer Ausgangspunkt für die Desktop-Portierung. Die Original-ZIPs befinden sich im separat übergebenen Gesamtpaket unter `sources/`. |
| VERIFIZIERT | `MAIN/state/USER_PROFILE_CURRENT.json` trägt `portable_revision=R13`. Das externe Profil und das Portable-Profil nennen R19. Beide `state/CHECKPOINT_LEDGER.json` in den ZIPs führen `system_version=3.4.6`, die externe Ledger-Datei 3.4.7. | Die Desktop-App übernimmt keine eingebetteten Profile, Provider-IDs, Checkpoints oder privaten Lernzustände. |
| ABGELEITET | `docs/TRANSLATION_CONTINUITY_NATIVE_v3.4.7.md`, `docs/TRANSLATION_ENGINE_FORCE_LOCK_v3.4.7.md` und `docs/USER_RELATIONSHIP_LEARNING_AND_EMOJI_CONTRACT_v3.4.7.md`. | Sprachpaar bleibt aktiv, unbekannte Texte stoppen sichtbar, lokale Korrekturen brauchen Bestätigung und Emojis ergänzen belegte Aussagen. |
| ABGELEITET | `compatibility_support/tests/linguistic_acceptance_stage04_cases.json` (30 direkte Profilfälle) und `compatibility_support/runtime/practical_output_renderer_v2_2_4.py` (Ausgabereihenfolge). | `data/r19.json` enthält die 30 Textpaare als exakte Profiltreffer. Historische Typografie und angehängte Deko-Emojis wurden bei der Ableitung entfernt. Die Testdaten sind keine neue menschliche Übersetzungsabnahme. |
| READBACK_PENDING | Kandidaten-Pointer `REPAIR_CARRIER_READY_NOT_PUBLISHED`, externe Handoff- und Ledger-Dokumente `PENDING_PUBLICATION`. | Kein produktiver Provider-Readback und keine Publikation. |
| OFFEN | `tests/MUM_REAL_HOST_ACCEPTANCE_v3.4.7.json`. | Abnahme in einem echten externen KI-Host bleibt separat offen. |
| OFFEN | Installation, Startmenü, Edge-App-Fenster und Deinstallation auf einem realen Windows-System. | Die Binaries wurden für Windows x64/ARM64 erzeugt. Eine Windows-Laufzeit war bei der Erstellung nicht verfügbar. |

`data/phrases.tsv` enthält neu erstellte lokale Phrasen, vier Basisprofile und keine privaten Nutzerdaten. Die Desktop-Version 1.4.0 ist eigenständig versioniert. Der Stand des nativen 666LINGUA-Systems ergibt sich aus dessen eigenem produktiven Pointer.

## Desktop-Prüfung

- Go-Tests für Satz- und Phrasentreffer, 30 R19-Profilfälle, Satzkomposition, Varianten, vollständige Blockade bei partieller Abdeckung, semantische Emojis, Zahlen-/Zeit-Anker, konfliktgeschützte lokale Korrekturen und Loopback-Anfragen.
- Headless-Chromium mit lokal laufendem Go-Backend. Geprüft wurden Start, Inhalte der fünf Ausgabepositionen, Kopieren in die Zwischenablage, Emoji-Verstärkung, Blockierung, Bestätigen, Ändern, Löschen, vorheriger Text, schmales Layout und Beenden.
- Windows-PE-Prüfung für AMD64 und ARM64, GUI-Subsystem und Prüfsummen. Das portabel gepackte Programm entspricht den jeweiligen Release-EXEs. Jedes Setup enthält bytegenau die passende Windows-App.

## Zusätzliche Prüfung für 1.1.0

- Go-Tests für Einstellungsdatei und Partner-Voreinstellungen, Sternzeichen-Grenzen, kalendarische Tages- und Jahreswechsel, Zeitdifferenzen und Sommerzeitlücke bzw. doppelte Stunde.
- Browser-Ende-zu-Ende mit frischem Profil und vollständigem Neustart des Dienstes. Getestet wurden englischer Erststart, automatischer DE-Speicher, unabhängiges Sprachpaar, Profil und Partner, Winterberg und New York, fortlaufende Uhren, Zielkalenderdatum, Umrechnung, lokale Profillöschung, 3.998 Emoji-Einträge, Ersetzen markierten Texts und Browser-Vollbild. Übersetzen, Kopieren und Lernen wurden erneut geprüft.
- Die OS-spezifischen Windows-Kiosk- und Installationsaufrufe wurden kompiliert. Der tatsächliche Setup- und Kiosk-Lauf auf Windows bleibt offen.

## Zusätzliche Prüfung für 1.2.0

- Neue Kontextregeln in `semantic.go`. Satzbelege und geprüfte Lesarten sind in der Oberfläche am Ergebnis sichtbar.
- Go-Tests für Begrüßung, Abschied, Bank und Flussufer, fehlenden bzw. widersprüchlichen Kontext, Segmentgrenzen und abweichende gespeicherte Fassungen. Test für Wiederverwendung und Löschung bestätigter Satzfolgen mit geschützter URL.
- Browser-Ende-zu-Ende und lokaler HTTP-Test für Kontextentscheidung, belegte Mehrdeutigkeit, Bestätigung und Wiederverwendung. Die ARM64- und x64-Setups sind crosskompiliert und als PE-Dateien geprüft. Der Installationslauf auf Windows bleibt offen.

## Zusätzliche Prüfung für 1.3.0

- Go-Tests für beide Wörterbuchrichtungen, die englischen Sprachvarianten, exakte Nachschlagebegriffe, Einsetzen in belegte Sätze, Vorrang bestätigter Fassungen, geschützte Kennungen, Bearbeiten und Löschen.
- Browsertest für beide Zwischenablage-Buttons, getrennte Einträge nach Richtung, Suche, Neuladen, Bearbeiten, Löschen und Wörterbuchbelege beim Übersetzen. Die x64- und ARM64-Setups wurden gebaut und als Windows-PE-Dateien geprüft. Ein Installationslauf auf Windows steht aus.

## Zusätzliche Prüfung für 1.4.0

- Die sechs Arbeitsbereiche Wörterbuch, Lernen, Zeitumrechnung, Systemnachweis, Belege und weitere Fassungen öffnen als modale Dialoge in derselben Ansicht.
- Browserprüfung bei 1920×1080, 1366×768, 1024×600, 800×600 und 400×680. Geprüft wurden Seitenhöhe, Quell- und Zieltext, internes Scrollen, Schließen und Rückkehr des Fokus zum Auslöser. Der Browservollbildmodus blieb beim Öffnen und Schließen des Zeit-Overlays aktiv.
- Go-Tests und Windows-PE-/Paketprüfung für x64 und ARM64. Eine echte Windows-Installation steht aus.
