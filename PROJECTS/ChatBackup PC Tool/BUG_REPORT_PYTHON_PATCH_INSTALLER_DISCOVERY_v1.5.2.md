# Bug Report — Python Patch Installer Discovery v1.5.2

## Beobachtung
Unter Windows wurde Python 3.12.10 korrekt gefunden. Der Bootstrap leitete aus dem python.org FTP-Verzeichnis dennoch 3.12.15 als vermeintlich installierbares Patchupdate ab und versuchte `python-3.12.15-amd64.exe` zu laden. Der Server antwortete 404.

## Ursache
Die bisherige Logik bestimmte die hoechste Patchnummer aus den FTP-Verzeichnissen. Ein vorhandenes Release-Verzeichnis beweist jedoch nicht, dass fuer diese Version ein Windows-Binaerinstaller veroeffentlicht wurde. Insbesondere Security-/Source-only-Releases koennen ohne Windows-Installer existieren.

## Reparatur
- Installer-aware Patchsuche: Kandidaten werden absteigend geprueft und nur Versionen mit tatsaechlich erreichbarem Windows-Installer akzeptiert.
- Patchupdate einer bereits kompatiblen Runtime ist best-effort statt startblockierend.
- winget bleibt bevorzugt.
- Bei nicht verfuegbarem optionalem Update wird die vorhandene kompatible Runtime weiterverwendet.
- Fehlendes/zu altes Python und Tkinter-Reparatur bleiben Pflichtpfade und verwenden ebenfalls die installer-aware Erkennung.

## Regression Guard
Ein FTP-Release ohne passenden `python-X.Y.Z-amd64.exe` darf nie wieder als installierbares Windows-Patchupdate behandelt werden.
