# R10 Integrationsaudit

## Quellen / Fundstellen
- `roshkins/IddSampleDriver` README: IddCx Windows Indirect Display Driver. **Nicht geeignet** für LED/SMART-Überwachung; keine Treiberinstallation.
- `AnalogJ/scrutiny` README und bereitgestelltes `scrutiny-master.zip`: SMART, Temperatur, historisches Tracking. **Adaptierte Ideen**: optionaler JSON-Leser und begrenzter Verlauf, kein Scrutiny-Backend gebündelt.
- `moabdrabou/Conky_Desktop_Guru` README: CPU/RAM/Disk/Network/GPU-Sichten. **Adaptiert**: kompakte native Windows-Tkinter-Ansicht (ohne Conky).
- `cespedesgarcia/pccommon` README: Windows WMI CPU/RAM/HDD/NVIDIA-NVAPI. **Nicht übernommen**: Nvidia-GPU-Zugriffe ohne Geräte-/Treiberprüfung.
- Hochgeladenes `SSD-LED-master.zip`: bereits in R2/R9 als funktionales Vorbild berücksichtigt; keine Doppelintegration.
- Hochgeladenes `HDDPerf-LED.zip`: 32/64-Bit-Binärdateien und ReadMe, mit Abtastrate, Prozentanzeige und Laufwerks-ID. **Nur Dokumentation ausgewertet, keine EXE ausgeführt.**

## Technische Trennung
- Datenträger-I/O ist keine SMART-Gerätegesundheit. Schwellwerte aus Durchsatz sind keine Ausfallvorhersage.
- SMART wird ausschließlich per ausdrücklich aktivierter Abfrage mit vorhandenem `smartctl`, `subprocess` ohne Shell, 8s Timeout gelesen; keine Autoscans.
- Fehlende SMART-Daten werden als `available=False` behandelt. Keine falsche Gesundmeldung.
- Desktop-Metriken bleiben read-only und brauchen keinen Display-/Kernel-Treiber.
- R9-Quelldateien in `src/klrw` werden unverändert kopiert. Separate R10-Module und Tests.

## Risiken / offene Abnahmen
- Native Win10/11 Tkinter-Anzeige nicht auf Windows validiert: READBACK_PENDING.
- Externe smartctl-Verfügbarkeit, Controller-Berechtigungen, NVMe/RAID/USB-Verhalten nicht auf Windows geprüft.
- SMART-Felder unterscheiden sich zwischen Geräten und Herstellerfirmware.
- Keine HDDPerf-Binaries integriert oder ausgeführt.
- Kein produktives GitHub-Write.
