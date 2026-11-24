---
name: sceeri-scriptable-ios
description: Schreibt, erklärt, auditiert und repariert JavaScript für Scriptable auf iPhone und iPad, einschließlich App-Skripten, Kurzbefehlen, Widgets und lokalen oder iCloud-Dateien.
---

# Scriptable auf iPhone und iPad

Route hierhin bei einem ausdrücklich genannten Scriptable-Ziel oder belegten iOS-Schnittstellen von Scriptable. Eine .js-Datei allein liefert noch keine Zielplattform. Nutze die [Engineering-Hierarchie](../../references/engineering-entscheidungshierarchie.md) für Verstehen, Audit, Reparatur, Verbesserung, Erweiterung und Neubau.

1. **Verstehen:** Binde vorhandenes Skript, Gerät soweit bekannt, vorgesehenen Startweg, Eingaben und Ausgaben. Verfolge Aufrufer → Eingabe → Scriptable-API → beobachtbare Ausgabe. Unterscheide interaktiven App-Aufruf, Kurzbefehle und Widget-Aufruf. Gemeinsame Fachlogik kann zwischen diesen Pfaden wiederverwendet werden.
2. **Auditieren:** Prüfe Kontextabfragen, Eingabeformat, Dateiquelle, Synchronisierung, Netzwerkantwort und Fehlerpfad. Verfolge ein Symptom zuerst zum zuständigen Aufruf. Ein eingegebener Widget-Parameter, eine geladene Datei und ein tatsächlich gerendertes Widget sind unterschiedliche Belege.
3. **Ändern:** Erhalte vorhandene Skriptnamen, Kurzbefehl-Ein- und Ausgaben, benutzte Pfade, gespeicherte Formate und das relevante Verhalten. Bei einem Fehler repariere die belegte Ursache. Bei einer Verbesserung definiere den beobachtbaren Gewinn. Neue Startwege ergänze passend zum Auftrag.
4. **Abnehmen:** Prüfe die Fachlogik mit harmlosen lokalen Fixtures, wenn sie sich vom Host trennen lässt. Syntax- und Fixture-Tests belegen diese Ebene. Für eine beauftragte Geräteabnahme führe den tatsächlichen Startweg auf iOS aus und prüfe Eingabe, Ergebnis und den relevanten Fehlerfall. Wenn das Gerät nicht zugänglich ist, gib einen kurzen reproduzierbaren Testweg an.

Verwende das [Laufzeitprofil](references/laufzeitprofil.md) für iCloud, Widgets, Kurzbefehle, Netzwerk und Geheimnisse.
