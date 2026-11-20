# Lokale Build-Eingaben

| Datei | Bezugsquelle |
| --- | --- |
| `g-helper-0.294.src.zip` | Beim Build aus dem offiziellen v0.294-Quellarchiv geladen. Das ursprünglich übergebene ZIP wird ebenfalls akzeptiert. |
| `windowsdesktop-runtime-10.0.15-win-x64.exe` | Beim Build von Microsoft geladen. |
| `PawnIO_setup.exe` | Beim Build aus dem offiziellen PawnIO-Release 2.2.0 geladen. |
| `ASUSSystemControlInterfaceV3.exe` | Einmalig aus dem bisherigen PC-Kompilierungspaket übernehmen oder Version **3.1.73.0** bei [ASUS Support](https://www.asus.com/supportonly/myasus/helpdesk_download/) beziehen. Falls der Download ein Archiv ist, die passende EXE daraus ablegen und wie in der Tabelle benennen. |

Der erwartete SHA-256 für die ASUS-EXE ist `3b429534f643ee6b22a3ad6bdbe9b7f97962d01dc791bdff4e76c6aea3b2f46c`.

Alle Prüfsummen und automatischen Bezugsquellen stehen in `../build-config.json`. Die Eingabedateien und der Ausgabeordner sind lokal. Der gebaute Installer enthält die für die Offline-Installation nötigen Dateien.
