666SOUNDsDESIGn MP3-MANAGER v2.5 – NEON EDITION

DATEIEN ORIGINAL VOM NUTZER:
 assets/app.ico = Windows-App-Icon
 assets/banner.png = breiter Kopf-Banner (2048x682)
 assets/logo.png = internes Logo (1254x1254)

START:
 Windows, Python 3 und Abhaengigkeiten aus requirements.txt benoetigt.
 Installiere nur nach eigener Entscheidung: py -3 -m pip install -r requirements.txt
 Danach STARTEN.bat starten. Diese Datei installiert NICHT heimlich.

AUSSEHEN:
 Neon Pink/Cyan/Lila, Dark Theme, skalierter Banner und internes Logo.
 Komplettes Fenster hat vertikalen Scrollbereich fuer kleinere Fenster.
 Dateitabelle behaelt eigene horizontale und vertikale Scrollbars.
 Bilder werden im Originalverhaeltnis verkleinert (nicht verzerrt).

PORTABLE EXE AUF WINDOWS:
 BUILD_PORTABLE_EXE.bat auf Windows starten (ggf. PyInstaller installieren).
 Binaerdatei in dist/666SOUNDsDESIGn_MP3_Manager.exe.
 Icon und beide PNGs werden via --add-data eingebettet.
 FFmpeg und FFprobe sind fuer Audio-Konvertierung weiterhin noetig.

FUNKTIONEN DES BESTEHENDEN PROGRAMMS BLEIBEN VORHANDEN:
 Dateinamenbereinigung, ID3-Metadaten, Sicherung, Kollisionsschutz,
 WAV/MP3 nach MP3 mit Parametern und Lautheitsnormalisierung, Systemcheck,
 CSV und C2PA-Warnhinweis.

SICHERHEIT:
 Vor Massenbearbeitung Vorschau und Testordner nutzen.
 Keine bestehenden Dateien ueberschreiben.
 ID3-Edits koennen C2PA-Nachweise ungueltig machen.

STATUS:
 Python-Syntax und GUI-Start unter Linux/Xvfb testbar; native Windows-GUI
 und Windows-EXE-Build sind nicht verifiziert.


=== v2.6 BATCH SYSTEM CHECK / PYTHON 3.15 REPAIR ===
STARTEN.bat erkennt Python, erstellt .venv und prueft Paketversionen und native Pillow-Importe.
Nach ausdruecklicher Bestaetigung werden nur Pakete in .venv installiert/aktualisiert.
Pillow>=13 fuer Python 3.15; PyInstaller>=6.21 fuer Python 3.15.
FFmpeg und FFprobe werden geprueft, aber NICHT automatisch installiert.
Fehlende ffmpeg.exe/ffprobe.exe: vom offiziellen Anbieter separat beziehen und in Projektordner legen.
BUILD_PORTABLE_EXE.bat prueft / installiert Build-Pakete nach Zustimmung und erzeugt die EXE lokal unter Windows.
Bereits installierte Python-Umgebungen ausserhalb .venv werden nicht veraendert.


V2.7 FIX: Python 3.15 Alpha wird blockiert. STARTEN.bat und BUILD_PORTABLE_EXE.bat nutzen neu die .venv_stable mit Python 3.11-3.14 final. Die alte .venv bleibt unberuehrt. Wenn stabile Python-Version fehlt: Python 3.13 installieren und erneut starten. Pakete nur nach Bestaetigung installieren.


NEU IN v2.8: Vier GUI-Reiter und dauerhafte drei Fortschrittsbalken. Die Fortschrittsanzeige "GESAMT" bezieht sich auf den aktuell gestarteten Vorgang (Audio oder Umbenennung). Der Windows-Starter aus v2.7.3 bleibt erhalten.


UPDATE v2.11: Neuer LYVRA-Header, kompakteres Layout und maximierter Start.


UPDATE v2.12: Offizieller Toolname: L.Y.V.R.A. - MP3 MANAGER


v2.19: Dateien per Drag & Drop in alle vier Reiter ziehen. Der ablösbare DATEIMANAGER ist aus jedem Reiter erreichbar. JPEG-Cover 512x512, Qualität individuell oder gesammelt; Quelle/Titel in beide Richtungen. C2PA nur nach Freigabe bearbeiten.


v2.22: Metadaten-Reiter zeigt Zielauswahl an. Cover vor Speicherung prüfen; bei C2PA geschützten Dateien explizit freigeben.


v2.23: Fehlerhafte Build-Abhaengigkeitsliste korrigiert (tkinterdnd2).

UPDATE v2.29: MP3-Konvertierung schreibt bereinigte Titel und die Metadaten-Maskenwerte automatisch in die neue MP3.


v2.30: Automatisch vertikal scrollbare Hauptreiter; Header dynamisch; Fortschritt unten fest. Dateiname → ID3-Titel nach Konvertierung.


v2.31: Presets im Audio-Reiter mit PRESET ANWENDEN. Externer Audio-Tool-Fix: REPARATUR_AUDIO_TOOLS.bat. Portable EXE: dist/tools neben der exe mitkopieren.


[v2.34] Audio Repair aus Original-WAV: siehe AUDIO_REPAIR_ANLEITUNG_DE.md.
