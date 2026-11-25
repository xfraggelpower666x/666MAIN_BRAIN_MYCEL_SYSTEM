# L.Y.V.R.A. – MP3 Manager v2.38

Quell-Freeze vom 18.11.2026. Native Windows- und Hörabnahme stehen aus.

| Grundlage | Verifizierter Stand |
| --- | --- |
| GitHub-Projektbasis | Branch `666MAIN_BRAIN`, Commit `266593b796bff9237d7a8c744607a553d8930819`, Projektbaum `7ccca96ca0a8a9c6ef83484c5a76baea05c5d52c` |
| Vorab-Sicherung | 67 Dateien gegen Git-Blob-IDs und ZIP-CRC geprüft. Wiederherstellbar aus dem genannten Commit. |
| v2.37-Handoff | SHA-256 `df56635daadaac99b83bfb170d69958f615647633b34b34b8ce55fcf1b40bcd9`. Historische v2.37-Berichte und Manifest gelten für dieses separate ZIP. |
| Restoration Lab | Anbindung, Anforderungen und gemeinsamer Starter stammen aus GitHub. Der eingefrorene Stand setzt die unveränderte Schwesterkomponente `Restoration-Lab-main` (Baum `7b82c1c09a6b2a7bedc7af20390911dd4fa6cfad`) voraus. |

## Abnahme

| Prüfung | Ergebnis |
| --- | --- |
| Python / FFmpeg | Python 3.12.14, FFmpeg/ffprobe 7.1.5 mit libmp3lame. Syntaxprüfung und fünf bestehende Prüfskripte für Audio-QC, Konvertierung, Reparatur, Fehlerfortschritt und statische Ordnerprüfung bestanden. |
| Neue Regressionen | Fünf pytest-Prüfungen bestanden, davon vier neue. Nachweise für konkurrierenden Export, Verwerfen bei QC-Fehler, linearen Balanced-Gain bei LRA 0, Audio-Drop-Dispatch und Portable-Build-Vertrag. |
| Windows | Zwei Windows-Batchtests auf Linux übersprungen. Native EXE, FFmpeg-Bundle auf Windows und PowerShell-Abnahme offen. |
| GUI | Tcl-Dispatch geprüft. Tk-Fenster, DPI/Mehrmonitor, Explorer-Drop und Overlay-UI benötigen einen Display-Host. |
| Restoration Lab | Backend importiert. Der Gesamtsystemcheck meldete auf diesem Linux-Host fehlendes PortAudio. |
| Klang | Die technische Abnahme verwendet erzeugte Audio-Testsignale. Die frühere Nutzer-WAV war in dieser Sitzung nicht abrufbar. Paariges WAV/MP3-Beispiel und Hörabnahme bleiben offen. |

## Fortsetzung

Unter Windows im vollständigen Quellprojekt `L.Y.V.R.A._MP3_MANAGER.bat build` ausführen. Danach die Schritte in [PORTABLE_ORDNERSTRUKTUR_DE.md](PORTABLE_ORDNERSTRUKTUR_DE.md) durchführen. Für den Hörvergleich die Original-WAV und die auffällige MP3 desselben Tracks mit Zeitmarke verwenden.

Für den Rücklauf ausschließlich die Projektänderungen dieses Releases im Git-Verlauf zurücknehmen. Projektbasis, Dateiinventar und Prüfsummen stehen oben und im v2.38-Manifest.
