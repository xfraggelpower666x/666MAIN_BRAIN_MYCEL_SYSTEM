# Windows Start — 666DEV Readback Repair

1. ZIP **vollständig in einen neuen Ordner** entpacken.
2. `START_WINDOWS_MENUE.bat` starten.
3. Menüpunkt **1** zur Diagnose verwenden. Das neue Paket hat noch keine `.venv`; vorhandene `.venv` aus der alten Version kann bei Bedarf mit Menüpunkt 2 neu erzeugt werden. **Nicht** die alte `.venv` kopieren: diese ist im Allgemeinen an den ursprünglichen Pfad gebunden.
4. Menüpunkt **2** (Setup) und nach Abschluss **3** (Update) für optionale Build-Tools verwenden. Bei bereits vorhandener Umgebung reicht Menüpunkt 3.
5. `TOOLS/REPORTS/TOOL_REPORT_*.json` enthält den Windows-Readback.

Wichtig: Kein Treiberinstall, kein Hardware-Schreibzugriff, keine automatische Neuinstallation von Python.

## R14 — Dynamische Anzeigen / Quellenintegration (22.11.2026)

Die erweiterte Laufwerksoberfläche (Menüpunkt E) bietet jetzt konfigurierbare R/W-Einheiten (KiB/s, MiB/s, MB/s, bit/s), 0–3 Dezimalstellen, kompakte/detaillierte Anzeige, Aktivitätsschwelle und Transparenz. Die Laufwerksliste ist scrollbar; USB-PDH-Counter werden bei Entfernen freigegeben und bei Wiederanschluss neu registriert. Bestehende Konfigurationen bleiben gültig.

Das Menü startet weiterhin mit `START_WINDOWS_MENUE.bat`; 2 richtet die `.venv` ein, E öffnet die Laufwerksverwaltung. **Kein automatischer USB-HID-Schreibzugriff.** Windows-Abnahme ausstehend.

Audit: `docs/R14_ARCHIVE_INTEGRATION_AUDIT.md`.


## R14 Tray Reparatur (Menüpunkt 4)
Menüpunkt 4 startet den Monitor mit Protokoll `TOOLS/REPORTS/TRAY_LAUNCH_LAST.log`. Bei fehlendem Tray-Backend erscheint das Desktop-Fenster als Fallback. Bei anderem Fehler werden Exitcode und Log im Menü angezeigt. Menüpunkt 5 bleibt der sichere Vorschautest.

## R15 Cyber Neon Drive Overlay (additive Erweiterung)
- Neues Overlay-Layout in **Menuepunkt E**: `vertical` (untereinander, Namen plus I/O-Details) oder `horizontal` (nebeneinander, nur Laufwerkskuerzel und eine LED).
- **Eine LED pro Laufwerk**: Cyan = Lesen, Pink = Schreiben (Schreiben hat Prioritaet), dunkel = ruhig/nicht zugeordnet.
- Aktivitaetslogik: konfigurierbare Mindestschwelle in KiB/s, adaptiv gelernte Grundlast, konfigurierbare Impulszeit und Ruhezeit.
- Dunkelgrau/Cyan/Lila/Pink in Drive Workspace und Overlay; alle bisherigen Mess-, Tray-, Hotplug- und Tastaturfunktionen erhalten.
- **Layout** im Laufwerksfenster auswaehlen und `Anwenden` betaetigen. Fuer Impuls/Ruhe im unteren Bereich Werte auswaehlen, `Anwenden`.
- Die bereits lokal gespeicherten Laufwerksselektionen bleiben bestehen (Schema v1 und alte JSON lesbar).
- Windows-Hardwaretests weiterhin noetig; 277 lokale Python-Tests bestanden.
