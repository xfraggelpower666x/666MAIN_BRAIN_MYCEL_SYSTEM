# Light Wave Tech 0.1.2 · Repair R01

Basis-Archiv SHA-256
`ea23ba69ba5ffec794ee8f062a55d212a48e5e01d5ede69062c5e60cf7e5940f`

- Der Stereo-EQ-Einstieg lädt Konfiguration und Caches relativ zu seiner Skriptdatei aus `CONFIG/`.
- Der Normal-Generator liest `CONFIG/filepaths.json` und erzeugt `CONFIG/preloaded_paths_cache_normal.json` unabhängig vom Aufrufordner. Er ersetzt den vorhandenen Cache erst nach vollständigem Schreiben. Fehlende Neural-Indexdateien oder weniger als zwei Videos in einem der beiden Hauptpools führen vor dem Schreiben zu einem Fehler.
- Die Sortierung behandelt numerische Videonamen zuerst nach Zahlenwert und anschließend benannte Dateien alphabetisch ohne Beachtung der Groß-/Kleinschreibung.

## Start und Abnahme

1. ZIP entpacken und `HOWTO_SETUP.txt` für die Python-3.10-Umgebung und die Medienzuordnung verwenden. Pfade für die Medien und die Playlist lokal konfigurieren.
2. Den Normal-Cache mit `python CONFIG/config_preload_path_names.py` erzeugen.
3. Aus dem Projektordner mit `python 32-bit_STEREO_EQ__light_wave_tech_v1.1.10.py` starten. Andere Assets können weiterhin vom Projektordner oder von absoluten Pfaden abhängen.

Die isolierte Prüfung unter Linux/Python 3.12 deckt die drei Fehlerfälle und das Lesen des neu erzeugten Caches ab. Die Medien-Testdateien prüfen die Dateiauswahl und Sortierung. Der vollständige Start mit echten Audio-/Videodateien, GPU und Python 3.10 sowie die Windows-Abnahme bleiben offen.

Die ursprünglichen Lizenz- und Attributionstexte liegen bei.
