---
name: sceeri-ffmpeg
description: Integriert, auditiert und repariert FFmpeg und FFprobe in Audio- und Videoprojekten, einschließlich Codecs, Filterung, Analyse, Fehlerbehandlung und Offline-Auslieferung.
---

# FFmpeg und FFprobe

1. Erfasse Eingabe, Zielcontainer, Codec, Stream-Auswahl, Kanalbelegung, Sample-Rate oder Bildrate und relevante Metadaten. Prüfe die tatsächliche Toolchain, ihren Build und die notwendigen Decoder, Encoder, Filter, Demuxer und Muxer. Ein vorhandener Encodername ersetzt keinen Test mit einem repräsentativen Zielmedium.
2. Prüfe den Eingabemedienstrom mit FFprobe und maschinenlesbarer Ausgabe. Baue FFmpeg-Aufrufe mit strukturierten Argumenten statt aus frei zusammengesetztem Shell-Text. Definiere Stream-Mapping, Ausgabe- und Überschreibregeln bewusst. Unterscheide Remux, Transkodierung und Filterung. Erhalte Originaldateien und vereinbarte Metadaten. Bei Audio-Werkzeugen prüfe bei Bedarf Kanäle, Pegel, Clipping, Dauer und Zielcodec mit relevanten Eingaben.
3. Handle Exitcode, lesbare Fehlermeldung, Zeitlimit, Abbruch und Teilresultate. Veröffentliche Ausgaben erst nach erfolgreicher Verarbeitung und passender Gegenprüfung. Nutze bei Fortschritt den beobachteten Tool-Status und bei parallelen Aufträgen getrennte Ausgabepfade.
4. Für Offline-Builds inventarisiere die verwendeten ausführbaren Dateien und Begleitbibliotheken inklusive Architektur, Quelle, Version, Integrität und Weitergabebedingungen des konkreten Builds. Prüfe Lizenztexte und gegebenenfalls Quellcodebereitstellung gemäß der verwendeten Distribution. Verwende im Produkt den verifizierten Paketpfad und prüfe die benötigten Funktionen auf dem Zielsystem ohne vorinstalliertes FFmpeg. Entwicklungs-Fallbacks nur gemäß Projektvertrag. Portable und Installer nutzen die mitgelieferten Werkzeuge gemäß den [Windows-Auslieferungsprofilen](../../references/windows-auslieferungsprofile.md).
5. Bei Electron startet Main oder ein geeignetes Backend FFmpeg aus dem gepackten Ressourcenverzeichnis. Renderer-Aufträge laufen über den engen [Electron](../sceeri-electron/SKILL.md)-IPC-Vertrag. Gib Status und Abbruchmöglichkeiten kontrolliert zurück.
