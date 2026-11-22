# Windows LED Remapper — Architektur- und Sicherheitsvertrag

## Eingänge
SystemSampler liest nur Betriebssystem-Telemetrie via psutil. Das Konfigurationsschema ist explizit auf Version 1 begrenzt; keine Script-Ausführung, Netzwerkendpunkte oder Plugin-Imports durch Benutzerkonfiguration.

## Datenfluss
Sampler → Sample → RuleEngine → LED-Zielzustände → Backend. Das GUI konsumiert Statusdaten über thread-sichere Queue; Tk wird nur im UI-Thread aktualisiert. CLI ist unabhängig vom GUI. Keine Hintergrundservices nach Programmende.

## Rechte / Sicherheitsgrenzen
PreviewBackend ist Standard. HardwareBackend ist nur unter native Win32 mit expliziter Zustimmung erreichbar. Es erzeugt synthetische CapsLock/NumLock/ScrollLock-Tastendrücke, keine direkte RGB-Hardwaresteuerung. Dies ändert Tastenfunktionen und kann mit Nutzeraktionen konkurrieren. Der Ausgangszustand wird bei ordentlichem Beenden bestmöglich wiederhergestellt. Bei systemweitem Neustart/Crash keine Garantie. Kein Anspruch auf beliebige Tastaturmodelle.

## Erweiterungspunkte
Neue Sensoren im Sampler und der Sample-Struktur ergänzen, dann Typvalidierung in `model.py` und Tests. Für RGB: **separates** SDK-Backend (z.B. spezifisches Vendor API), strikt hardwaremodellgebunden und optional; bestehendes Win32-Lock-Backend unverändert lassen. Persistenter Autostart bleibt bewusst outside scope.

## Validierung vor Produktiveinsatz
Windows 10/11 mit realer Tastatur prüfen: eingebaute und externe Tastatur, USB/Bluetooth, Eingabe bei Caps/Num, RDP, Sleep/Resume, mehrfache Start/Stop-Zyklen, Counter reset, parallel manuelle Tastenbetätigung. Hardware-Risiken separat dokumentieren. Keine Aussage „hardware verified" ohne diese Tests.
