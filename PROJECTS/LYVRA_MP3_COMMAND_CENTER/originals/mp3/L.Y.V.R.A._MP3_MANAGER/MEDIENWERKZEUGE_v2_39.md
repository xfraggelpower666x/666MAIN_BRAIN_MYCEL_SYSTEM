# L.Y.V.R.A. MP3 Manager v2.39 – Medienwerkzeuge

Nach dem vollständigen Entpacken `MP3_MANAGER_START.bat` starten und Menüpunkt 1 wählen. Im **Audio-Browser** auf **MEDIENWERKZEUGE** klicken.

- Datei wählen und die gewünschte **Audiospur** anhand von Index, Codec, Kanalzahl und Sprachkennung auswählen.
- **MP3** erzeugt einen Stereo-Export mit 320 kbit/s. **WAV** speichert PCM mit 24 Bit und behält Abtastrate und Kanalbelegung der gewählten Spur bei.
- **MP4** erstellt ein H.264/AAC-Covervideo mit 720p oder 1080p. Bis zu zwölf JPG-, PNG- oder BMP-Bilder wählen. Die Pfeile ändern die Reihenfolge. Überblendungen lassen sich abschalten.
- Während die Kodierung läuft, zeigt der Dialog die verarbeitete Medienzeit und bei bekannter Dauer eine Schätzung der Restzeit an. Per **Stopp** lässt sich der Job abbrechen. Ausgaben werden erst nach Überprüfung der Streams und vollständigem Dekodiertest freigegeben. Bestehende Zieldateien werden nicht ersetzt.

Der separate MP3-Workflow, die Presets, ID3-Verarbeitung und Restoration Lab bleiben verfügbar. **Maximum Quality** und **Original Preserve** haben keine Normalisierung. Die Medienwerkzeuge verwenden ebenfalls keine Normalisierung.

## Abgleich der elf Eingabearchive

| Eingabe | Befund und Umsetzung |
| --- | --- |
| MP3 Manager v2.38 | Basisarchiv vollständig übernommen. SHA-256: `c4b3252037461e94e170b546e8a8f6d9a8d2b5fd74799df38309d859b307623e` |
| MediaToolkit Master, Features, MajorRefactoring | Medienprobe, Stream-Auswahl und FFmpeg-Export mit eigener Python-Implementierung. Die enthaltenen 32-Bit-Binärdateien, darunter FFmpeg 4.2.1, bleiben außerhalb der Auslieferung. |
| ffmpegfs 2.50 ZIP und TAR.GZ | FUSE-Quellarchive. Die 76 gemeinsamen Dateien unter `src/` sind bytegleich. Kein FUSE-Mount im Windows-Starter und keine FFmpeg-Runtime aus diesen Archiven. |
| mp3ToMp4 | Export mit mehreren Bildern und Überblendungen lokal umgesetzt. |
| mp4-to-mp3-frontend | Konvertierung in den vorhandenen Desktop-Ablauf übernommen. Browser-Frontend, Login und Firebase sind für diesen Ablauf nicht erforderlich. |
| Better FFmpeg Progress | Maschinenlesbare Medienzeit und ETA in den Medienwerkzeugen und beim bestehenden MP3-Export umgesetzt. |
| audio_transcriber | Konvertierung zur Vorbereitung von WAV umgesetzt. Die Transkription der Vorlage ruft `recognize_google` auf und ist nicht Teil des lokalen Exports. |
| ByzleMP3 | Vorlage mit FFmpeg im Hintergrund. Medienjobs im Desktop-Fenster laufen abbrechbar im Hintergrund. YouTube-Down­loader, Web-Backend und Redis-Queue sind in diesem Paket nicht eingebunden. |

## Prüfung

Getestet unter Linux mit FFmpeg/FFprobe 7.1.5. Reale Kodierungen und Dekodierungen mit einem Video mit zwei Tonspuren sowie einem Zwei-Bilder-Covervideo mit und ohne Überblendung. Geprüft wurden außerdem Abbruch, Dateikollisionen und die v2.38-Audioregressionen.

Das ZIP enthält das Windows-Quellpaket mit Start-Batch. Native Windows-GUI, PyInstaller-EXE und Windows-FFmpeg-Bundle bleiben separat auf Windows zu prüfen.
