# MP3 Manager v2.40

Basis ist das geprüfte v2.39-Quellpaket mit SHA-256
`a2b6db30e956768231f018ccb2962e056db4d50db3c0e3fe1b33316281567c2e`.

## Reparaturen

- Covervideo: Fehlt die Dauer der ausgewählten Audiospur in FFprobe, ermittelt FFmpeg sie durch Dekodieren genau dieser Spur. Dabei beginnt deren Zeitachse bei null. Das letzte Bild kann bis zum Ende der Spur stehen bleiben, auch bei Rundung auf ganze Videobilder.
- Fortschritt: FFmpeg-Meldungen werden pro Fortschrittsblock ausgewertet. Der ältere Schlüssel `out_time_ms` wird in Mikrosekunden ausgewertet, wenn `out_time_us` fehlt. Die verarbeitete Medienzeit läuft nicht rückwärts.
- Stopp: Gilt jetzt auch während der Medienprüfung. Dauerermittlung, Kodierung und Ausgabeprüfung werden im Dialog als eigene Schritte angezeigt.
- Zielschutz: Ein vorhandener symbolischer Link gilt auch mit fehlendem Linkziel als Kollision.
- Die drei erneut gelieferten Archive Better FFmpeg Progress, ByzleMP3 und MP4-to-MP3-Frontend sind jeweils SHA-256-identisch zu ihren vorherigen Fassungen.

## Abnahme

Unter Linux mit FFmpeg/FFprobe 7.1.5 wurden 12 pytest-Prüfungen und fünf bestehende Prüfskripte erfolgreich ausgeführt. Zwei Windows-Batchtests wurden übersprungen. Der Covervideo-Test mit acht Sekunden Containerdauer und 2,03 Sekunden Audio schlug unter v2.39 fehl und prüft jetzt erfolgreich auch die Bildfarbe bei 1,8 Sekunden. Abbruch mit altem Fortschrittsschlüssel und Kollision mit einem hängenden symbolischen Link wurden zusätzlich geprüft.

Zum Quellstart das ZIP vollständig entpacken und die oberste `MP3_MANAGER_START.bat` starten. Beim Windows-Build gelten die vorhandenen Anforderungen an Python und FFmpeg. Ein nativer Windows-Start und eine gebündelte EXE sind in dieser Abnahme nicht nachgewiesen.
