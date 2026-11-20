# Repair v1.10.5 · 2026-11-14

## Änderungen

- Der PC-Parser erkennt servergerenderte Transkripte und bewahrt Rollen, belegte HTML-IDs, Reihenfolge, Wiederholungen und direkt referenzierte Bilder.
- Die Windows-Laufzeitprüfung instanziiert die reguläre `.pyw`-GUI und öffnet ihren Browser-Recovery-Dialog. Die kombinierte Abnahme verwendet den vom Bootstrap ausgewählten Python-Interpreter durchgängig.
- Die Release-Prüfung liest die Pfade im äußeren PC-Manifest und meldet fehlende oder veränderte Dateien.
- Der eingebettete Scriptable-Companion v1.0.9 verwendet denselben Importpfad im normalen Menü und in der Abnahme. Version 1.0.8 bleibt unter `mobile_scriptable/history/` erhalten.

## Start und Abnahme

1. Windows-Archiv vollständig entpacken und `START_TOOL.bat` starten.
2. `VERIFY_WINDOWS_HOST_ACCEPTANCE.bat` mit einem öffentlichen Share ausführen.
3. Auf dem iPhone v1.0.9 einspielen und in Scriptable Diagnostics / Self-Test → Run host acceptance wählen. Den früher problematischen Share erneut testen.
4. Windows-EXE bei Bedarf mit `BUILD_EXE.bat` erzeugen und mit `START_EXE.bat` auf dem Zielhost starten.
