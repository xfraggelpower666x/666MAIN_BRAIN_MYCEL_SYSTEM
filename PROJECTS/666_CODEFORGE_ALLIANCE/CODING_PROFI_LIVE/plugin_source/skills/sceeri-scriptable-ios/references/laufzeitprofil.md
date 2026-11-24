# Scriptable-Laufzeit und Gegenproben

| Einstieg | Eingabe, Ausgabe und Abnahme |
| --- | --- |
| App | Interaktive Auswahl nur verwenden, wenn sie in diesem Ablauf sinnvoll ist. Prüfe Abbrechen und Rückkehr sowie die sichtbare Ausgabe. |
| Kurzbefehl | `args.shortcutParameter` prüfen und Ausgabe gemäß vereinbartem Vertrag über `Script.setShortcutOutput` oder den unterstützten Rückgabewert liefern. Teste fehlende Eingabe und nachfolgende Aktion. |
| Widget | `args.widgetParameter` und Widget-Kontext prüfen. Gib ein `ListWidget` über `Script.setWidget` aus. Halte die Darstellung kompakt und prüfe verfügbare Widget-Größen. Die Aktualisierungszeit wird maßgeblich durch iOS bestimmt. |

- **Dateien:** Wähle bewusst `FileManager.local()` oder `FileManager.iCloud()`. Unterscheide fehlende Datei, noch ausstehendes iCloud-Download und ungültigen Inhalt. Bei einer vorhandenen iCloud-Datei den nötigen Download abwarten, dann lesen. Erhalte Aufrufer, Datenformat und Benutzerdateien bei einer Änderung.
- **Netzwerk:** Verwende Scriptables `Request` für HTTP-Aufgaben, sofern es zum Skript passt. Prüfe relevante HTTP-Status, Timeouts und erwartete Nutzlast separat. Ein frischer Erfolg, ein alter Cache und eine fehlende Quelle sollen unterscheidbar sein. Ein Cache kann bei einem geeigneten Auftrag als Fallback dienen. Seine Ausgabe trägt den Zeitpunkt des letzten erfolgreichen Abrufs.
- **Zugangsdaten:** Verwende den Keychain für benötigte Zugangsdaten. Prüfe Vorhandensein vor Zugriff. Gib Geheimnisse weder im Skriptbeispiel noch in Widget, Kurzbefehlsausgabe oder Logs aus.
- **Ursachentest:** Trenne ungültige Eingabe, iCloud-Wartezustand, HTTP-Fehler, ungültige Daten und Darstellung. Ändere jeweils eine relevante Bedingung. Neue Rückfallwege aus mehreren Befunden sind Vorschläge, bis eine geeignete Gegenprobe die gewünschte Wirkung trägt.

Beispiel für eine Chat-Abnahme: Ein Webradio-Statuswidget zeigt bei erfolgreicher Antwort den vereinbarten Track und die Abrufzeit. Bei Fehler wird ein vorhandener alter Wert als solcher gezeigt oder ein sinnvoller Offline-Zustand verwendet. Der echte Endpunkt und sein Format kommen aus dem Zielprojekt.

## Referenzen

- [Scriptable-Dokumentation zu Args](https://docs.scriptable.app/args/)
- [Scriptable-Dokumentation zu Script](https://docs.scriptable.app/script/)
- [Scriptable-Dokumentation zu FileManager](https://docs.scriptable.app/filemanager/)
- [Scriptable-Dokumentation zu Request](https://docs.scriptable.app/request/)
- [Scriptable-Dokumentation zu ListWidget](https://docs.scriptable.app/listwidget/)
- [Scriptable-Dokumentation zu Keychain](https://docs.scriptable.app/keychain/)
