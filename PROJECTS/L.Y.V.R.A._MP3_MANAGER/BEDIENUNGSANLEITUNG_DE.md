# L.Y.V.R.A. - MP3 MANAGER · Bedienungsanleitung v2.20

## 1. Start und Voraussetzungen
ZIP entpacken und `STARTEN.bat` ausführen. Der Starter prüft Python, Pillow, Mutagen und tkinterdnd2 in einer getrennten `.venv_stable`-Umgebung. FFmpeg/FFprobe sind für Audiokonvertierungen erforderlich. Installationen nur nach Zustimmung. Für einen externen Windows-EXE-Build `BUILD_PORTABLE_EXE.bat` im Projektordner starten; in der fertigen EXE existiert **kein** EXE-Builder.

## 2. Dateien und Umbenennen
Musikordner auswählen und »Ordner prüfen« betätigen. WAV- und MP3-Dateien erscheinen gemeinsam. Die permanente Bestandsleiste zeigt Gesamt, MP3, WAV und Auswahl. »Nur Dateinamen umbenennen« verändert keine Audio-Tags. »Dateinamen + ID3-Titel bereinigen« kann bei MP3 auch die Titel-Tags anpassen. Zeitblöcke wie `[0m00s-4m56s]` werden entfernt; `(1)` wird bei aktivierter Option zu `1`. Vorschau und Sicherungen nutzen; niemals bereits existierende Zieldateien überschreiben. STOPP stoppt zwischen Dateien.

## 3. Metadaten und Cover
Dateien markieren oder »Alle Dateien im Ordner« auswählen. Nur mit Häkchen ausgewählte ID3-Felder werden geändert. Titelübernahme erfolgt pro Datei: Dateiname → ID3-Titel oder ID3-Titel → Dateiname. »METADATEN STARTEN / SPEICHERN« schreibt ausschließlich MP3-Metadaten und Cover; Dateinamen bleiben dabei unverändert. Vorher wird gesichert. WAV-Metadaten werden nicht als ID3 behandelt.

Cover: »Ein Cover für alle gewählten MP3« oder »Cover nur für markierte MP3« wählen und »Cover einbetten/ersetzen« aktivieren. Das Bild wird zu 512 × 512 Pixel JPEG. Qualitätsregler 1–100 (Standard 95). Drei Modi: **Einpassen** (Balken), **Zentriert zuschneiden** (Bildteile können verloren gehen), **Dehnen** (Windows-Hintergrund-Stil; Bildverhältnis wird bewusst verzerrt). Auch ein 16:9-Bild wird im Dehnen-Modus vollflächig quadratisch. Coveränderungen können bestehende C2PA-Provenienznachweise ungültig machen; deshalb sind solche Änderungen ohne ausdrückliche Freigabe gesperrt.

## 4. Audio-Konvertierung
Quellformat WAV, MP3 oder GEMISCHT wählen. Zielprofil nach Wunsch: Standard 48000 Hz / 320 kbit/s / Stereo, optional Normalisierung −14 LUFS und True Peak −2 dBTP. `s16p` bezeichnet das PCM-Zwischenformat, nicht die Bit-Tiefe der MP3. WAV→MP3 ist verlustbehaftet. MP3→MP3 kann keine verlorenen Klanginformationen zurückbringen. Prüfe Ausgabe und Lautheit nach dem Umkodieren. STOPP beendet laufende FFmpeg-Aufträge; nur unvollständige Ausgaben werden entfernt.

## 5. Audio Labs
Der Reiter AUDIO LABS startet Suno Song Remaster, Restoration Lab, SunoCleanser und die MP3Gain-VB6-GUI; Sunscreen und wav2mp3 laufen als Kommandozeilenwerkzeuge. Im Quellprojekt müssen die Projektordner neben dem MP3-Manager unter `PROJECTS` liegen. Suno benötigt lokale Electron-Abhängigkeiten und einen Renderer-Build (`npm run build` im Projektordner); der Manager startet keinen Entwicklungsserver. Restoration Lab verwendet sein eigenes `STARTEN.bat` und SunoCleanser die Conda-Umgebung `sunocleanser`. MP3Gain ist Windows-only und benötigt `MP3GainGUI.exe` sowie den vollständigen Build `electron-bridge/release/win-unpacked` neben der GUI. Sunscreen akzeptiert MP3, WAV, FLAC und M4A; eine einzelne ausgewählte Datei wird mit `--smooth --widen --excite --match --master` verarbeitet. Die Ausgaben liegen im Ordner `sunscreen` neben der Quelle und sind 24-Bit-WAVs. wav2mp3 verarbeitet alle WAV-Dateien direkt im gewählten Ordner und legt die MP3-Ausgaben dort ab; der Manager startet es nicht, wenn gleichnamige MP3-Ausgaben vorhanden sind. Zum Bauen werden die C++- und LAME-Entwicklungsdateien aus dem Makefile benötigt. Für portable Builds werden vorhandene Apps, die MP3Gain-GUI samt Bridge sowie vorhandene Sunscreen- und wav2mp3-Windows-Binaries optional mitkopiert. Fehlende Pakete werden niemals still installiert. Die Manager- und VB6-Oberflächen verwenden die L.Y.V.R.A.-Palette aus Dunkelblau, Cyan, Pink und Violett.

## 6. Zwei Monitore und Drag & Drop
In jedem Reiter »DATEIMANAGER / 2. BILDSCHIRM« öffnen, Fenster auf anderen Monitor ziehen. Dateien/Ordner aus dem Explorer in die GUI ziehen. Der separate Live-Statusmonitor zeigt aktuelle Datei, Umbenennung, Audio und Gesamt. Die Anzeigen werden von aktiven Prozessen gespeist und können bei inaktiven Vorgängen 0 anzeigen.

## 7. System, EXE und Sprache
Der Reiter SYSTEM prüft Komponenten; der EXE-Build läuft **nur über die externe Batchdatei**. DE/EN oben im Hauptfenster auswählen. Hilfe über »? HILFE / HELP«. Dateinamen, Liedtitel, vom Benutzer eingetragene Texte und Metadaten werden bei Sprachwechsel niemals übersetzt.

## Sicherheit / Grenzen
Originale erhalten, Sicherheitskopien vor Schreibvorgängen; ZIP und Python-Quellcode zuerst testen. Nicht alle Windows-/DPI-/Drag-and-drop-/FFmpeg-Szenarien wurden auf einem echten Windows-PC geprüft. Logs bei Fehlern sichern. Nicht ungeprüft auf das komplette Musikarchiv anwenden: zuerst 2–3 Testdateien.


### v2.24 – Metadaten / Metadata
Metadaten-Start befindet sich oberhalb der Zieldateiliste. Titelübernahme pro MP3 schaltet die manuelle Songtitel-Eingabe aus. Der EXE-Build erfolgt außerhalb der Anwendung über BUILD_PORTABLE_EXE.bat.


### v2.24 – Metadaten / Metadata
Metadaten-Start befindet sich oberhalb der Zieldateiliste. Titelübernahme pro MP3 schaltet die manuelle Songtitel-Eingabe aus. Der EXE-Build erfolgt außerhalb der Anwendung über BUILD_PORTABLE_EXE.bat.
