---
name: sceeri-projektsprachen
description: Prüft und implementiert die Sprachauswahl Englisch und Deutsch für neue und bestehende Tools. Englisch ist Standard. Windows-Batch- und CMD-Texte sind immer Englisch.
---

# Projektsprachen und englische Windows-Starter

Wende diese Facette bei Neubau, Projekt-Audit, Repair und Verbesserung eines Zieltools an. Die Vorgabe gilt für das ausgelieferte Tool und seine Skripte. Sie bestimmt die Gesprächssprache im Coding Profi nicht.

## Tool

1. Erfasse die vorhandene Spracheinstellung, Locale-Dateien und sichtbaren Texte in Oberfläche, Hilfen, Status, Validierung und Fehlermeldungen. Prüfe die tatsächlich verwendeten Einstiege und den Standard beim ersten Start.
2. Verwende die bestehende Internationalisierung. Ergänze fehlende englische und deutsche Texte in derselben Struktur. Stelle eine auffindbare Auswahl **English / Deutsch** in Oberfläche oder Einstellungen bereit. Ein CLI-Tool erhält ein passendes Flag oder eine dokumentierte Konfiguration. Eine Bibliothek ohne eigene Benutzeroberfläche erhält einen passenden Locale-Einstieg für ihre nutzerseitigen Meldungen, sofern sie welche ausgibt. Vermeide eine zusätzliche Laufzeitabhängigkeit, wenn die vorhandene Struktur genügt.
3. Setze Englisch als Standard für frische Installationen und bei fehlender oder ungültiger Sprachwahl. Die Betriebssystemsprache überschreibt diesen Standard nicht. Erhalte ausdrücklich gespeicherte gültige Sprachwahlen. Bei fehlendem deutschem Text fällt der Eintrag auf den englischen Text zurück. Prüfe trotzdem die Vollständigkeit beider Sprachfassungen.
4. Bewahre Bezeichner, Pfade, Argumente, Protokollfelder, stabile Maschinen-Ausgaben und bereits vorhandene weitere Locales. Trenne technische Verträge von sichtbaren Texten. In einem ausdrücklich lesenden Audit dokumentiere die Abweichung als Befund. In einem beauftragten Neubau oder Repair korrigiere sie in der Arbeitskopie.

## Windows-Starter

Prüfe jede ausgelieferte .bat- und .cmd-Datei, auch vorhandene Skripte. Übersetze nichtenglische nutzergerichtete Texte, Titel, Menüs, Auswahlfragen, Fehlerhinweise und eigene Logtexte ins Englische. Neue Skripte verwenden auch in Kommentaren Englisch. Übersetze bestehende nichtenglische Kommentare, sofern sie keine geschützten Lizenz- oder Herkunftstexte sind. Erhalte Pfade, Dateinamen, Variablen, Befehlsargumente, Exitcodes und Aufrufer. Wenn die Buchstaben einer Auswahl geändert werden, prüfe Auswahlfolge, Zweiglogik und bestehende Schnittstellen zusammen. Durchgereichte Meldungen externer Programme können deren eigener Sprache folgen. Teste, dass die Sprachwahl des Zieltools die Starter-Texte nicht umschaltet.

## Abnahme und Lieferung

Prüfe einen frischen Start ohne Sprachwahl, Wechsel zu Deutsch, Rückwechsel zu Englisch, ungültige Sprache, Übersetzungsparität und Verhalten nach Neustart, wenn das Tool die Auswahl speichert. Prüfe in bestehenden Projekten, dass eine bereits ausdrücklich gewählte Sprache erhalten bleibt. Prüfe alle eigenen sichtbaren Batch-Texte und mindestens die relevanten Normal- und Fehlerpfade. Nutze die [Windows-Lieferabnahme](../../references/windows-lieferabnahme.md) und den [Projektabschluss](../../references/code-delivery.md#verbindlicher-projektabschluss). Weise Laufzeitnachweise und statische Prüfungen getrennt aus.
