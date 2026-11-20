# Bug Report — Long Chat Readback False Negative

## Status

`REPRODUCED -> ROOT_CAUSE_VERIFIED -> REPAIRED -> RE-AUDIT_PASS`

## Beobachtung

Bei einem längeren Share-Link-Chat meldete v1.1.0 nach dem Speichern:

> Die gespeicherte Datei stimmt nach dem Rücklesen nicht mit dem Export überein.

## Reproduzierte Ursache

`write_verified()` schrieb mit festem `newline="\n"`, las anschließend aber über `Path.read_text()` zurück. Der Textmodus verwendet beim Lesen Universal-Newline-Normalisierung. Enthält der Export `CRLF` (`\r\n`) oder einzelnes `CR` (`\r`), wird es beim Lesen zu `LF` (`\n`) normalisiert. Die Datei kann also korrekt geschrieben sein, während der Stringvergleich trotzdem fehlschlägt.

Reproduktion mit v1.1.0:

- LF-only: PASS
- CRLF: FAIL
- einzelnes CR: FAIL
- langer gemischter Chat: FAIL

## Reparatur v1.1.1

- Export wird als exakt kodierte Bytes geschrieben.
- Readback vergleicht zuerst die Byte-Länge.
- Danach wird SHA-256 des erwarteten Byte-Payloads mit einem gestreamten SHA-256 des gespeicherten Files verglichen.
- Keine Newline-Normalisierung findet während der Integritätsprüfung statt.

## Regressionstests

- LF-only: PASS
- CRLF: PASS
- einzelnes CR: PASS
- Unicode/Emoji: PASS
- 740.000-Byte Mixed-Newline-Test: PASS
- Core runner: 9/9 PASS
- Pytest: 10 PASS

## Scope

Parser, GUI-Struktur, Bootstrap, Speicherdialoge, TXT/MD/JS-Export und Startwege wurden nicht entfernt oder architektonisch ersetzt.
