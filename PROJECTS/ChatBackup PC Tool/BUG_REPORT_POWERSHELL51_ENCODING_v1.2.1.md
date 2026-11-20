# Bug Report — Windows PowerShell 5.1 Parser / Encoding

## Betroffen

- Version: v1.2.0
- Datei: `bootstrap/bootstrap.ps1`
- Symptom: Parserfehler an `NOT_REQUIRED`, fehlende Klammern/Braces und Folgefehler im Catch-Block.

## Ursache

Verifizierter Vergleich: v1.1.1 begann mit UTF-8-BOM `EF BB BF`; v1.2.0 begann direkt mit `[CmdletBinding()]` und hatte keinen BOM. Die v1.2.0-Bootstrap-Datei war damit UTF-8 ohne BOM und enthielt Unicode-Zeichen, unter anderem einen typografischen Gedankenstrich. Windows PowerShell 5.1 behandelt UTF-8 ohne BOM je nach Host/Codepage nicht verlaesslich als UTF-8. Dadurch wurden Zeichenfolgen beim Parsen verfaelscht.

## Reparatur v1.2.1

- UTF-8-BOM `EF BB BF` wiederhergestellt (entspricht der zuvor funktionierenden v1.1.1-Erkennung).
- `bootstrap.ps1` zusaetzlich vollstaendig auf ASCII-sichere Quellzeichen normalisiert.
- CRLF-Zeilenenden fuer Windows gesetzt.
- Keine Unicode-Typografie mehr im Bootstrap-Quelltext.
- Version und Abhaengigkeitsmanifest auf 1.2.1 aktualisiert.
- Automatischer Test stellt sicher, dass `bootstrap.ps1` ausschliesslich ASCII-Bytes enthaelt.

## Nicht veraendert

Parser, Export-Readback, GUI-Funktionen, Share-Link-Logik, lange-Chat-Reparatur und Bildassets bleiben erhalten.
