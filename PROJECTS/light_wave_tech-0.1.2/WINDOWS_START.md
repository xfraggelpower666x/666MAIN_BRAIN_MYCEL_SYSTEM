# Light Wave Tech 0.1.2 R01 · Windows-Starter

Entpacke das vollständige ZIP und öffne den Ordner `light_wave_tech-0.1.2`.
Doppelklicke auf `STARTEN.bat`. Im Menü sind Stereo-EQ-Start,
Voraussetzungsprüfung und Normal-Cache-Generator erreichbar.

1. Richte Python 3.10 und die Pakete nach `HOWTO_SETUP.txt` ein. Der Starter
   sucht in `.venv`, in der aktiven Python-Umgebung und über `py -3.10`.
2. Trage deine Medienpfade in `CONFIG/filepaths.json` ein und passe die
   Playlist-Pfade gemäß der Setup-Anleitung an.
3. Nutze im Menü zuerst **2** zum Prüfen, **3** zum Erzeugen des Normal-Caches
   und danach **1** zum Starten.

`PRUEFEN.bat` und `CACHE_ERSTELLEN.bat` sind direkte, unbeaufsichtigte
Einstiege für ein geöffnetes Terminal. Das Menü hält die Ausgabe nach einer
Aktion sichtbar. Die Prüfung erfasst Python-Version, importierbare Module
und lesbare Start-JSON-Dateien. Die vollständige Prüfung mit echten Medien,
OpenGL und Audiogerät erfolgt beim Anwendungsstart.
