# Windows-Lieferabnahme

| Eingabe oder Zustand | Gegenprobe |
| --- | --- |
| Vollständiges neues oder repariertes Windows-Projekt | Dokumentierten Starter aus einem frischen Pfad mit Leerzeichen prüfen. Ein bestelltes ZIP dazu zuerst entpacken. Normalen Einstieg beobachten und Projektprüfungen ausführen. |
| Starter aus einem anderen Arbeitsverzeichnis aufgerufen | Arbeitsverzeichnis und relative Ressourcen beziehen sich auf das entpackte Projekt. |
| Ausgefallener Launcher oder Test | Fehlphase und tatsächlicher Fehlercode bleiben bis zum Aufrufer erhalten. Pause, Protokollausgabe und Aufräumen überschreiben den Rückgabecode nicht. |
| Nicht kompatibler Interpreter oder fehlende Abhängigkeit | Konkrete Voraussetzung nennen und mit Fehlerstatus stoppen. Eine Installation erscheint nur als gesonderter Schritt. |
| Portable-Build | Prüfe tatsächliches Ausgabeziel, Vollständigkeit des Verzeichnisses und die dokumentierten Bestandteile. Prüfe die EXE in einer geeigneten Windows-Umgebung. |
| Audio-Tools | Prüfe FFmpeg und FFprobe getrennt und teste benötigten Codec oder Encoder. Eine Pfadexistenz allein belegt keine Funktion. |
| Nachweis ohne Windows | Prüfe Dateireferenzen, CRLF und Kontrollfluss statisch. Lies ein bestelltes ZIP zurück. Markiere Windows-Start und Fehlerpfade als OFFEN. |
| Unvollständiges Ausgangsprojekt | Liefere vorhandene Befunde und nenne fehlenden Einstieg, Dateien und Auswirkungen auf die Paketfreigabe. |

## Statische Befunde an den Vorlagen

- STARTEN(2).bat endet unabhängig vom Ablauf mit Exitcode 0. Die aufrufende Stelle kann damit den fehlgeschlagenen Start oder Abbruch nicht erkennen. Bei Vorprüfungen und dem Launcher den tatsächlichen Rückgabecode übernehmen.
- REPARATUR_AUDIO_TOOLS(1).bat prüft den gewünschten Encoder, beendet die Prüfpunkte anschließend aber bedingungslos mit Erfolg. Das Vorhandensein der Werkzeuge und die Codec-Prüfung müssen getrennt ausgewertet werden.
- BUILD_PORTABLE_EXE(2).bat verweist auf PYTHON_STABLE.bat und SYSTEM_CHECK.py. Prüfe diese Ziele im Kandidaten und gleiche den gemeldeten EXE-Pfad mit dem tatsächlichen Build ab. Der Name im Beispiel gilt nur für das Originalprojekt.
- PORTABLE_VERIFY(1).bat hängt von PORTABLE_VERIFY.ps1 ab und setzt die PowerShell-Ausführungsrichtlinie für den Aufruf auf Bypass. Verwende bei einem neuen Starter eine im Zielprojekt zulässige Ausführungsweise und liefere den tatsächlichen Verifizierer mit.
- PYTHON_STABLE(1).bat übernimmt die Trennung der vorhandenen Umgebung als Ausgangsmuster. Die erlaubte Interpreter-Version kommt aus dem Zielprojekt. Die vorhandene Umgebung bleibt bei Inkompatibilität erhalten.
- START_RADIO_WAVE_DIAGNOSTIC.cmd trennt EXE-Pfad, Warten und Rückgabecode. Das dort genannte Startup-Log stammt aus dem Zielprogramm und ist beim fehlenden Log kein Beleg für eine konkrete Ursache. Erhalte relevante frühere Diagnosebelege.

Das Browser-Archiv diente als Architekturquelle für mehrschrittige Planung und Fortsetzung. Dafür sind Engineering-Zyklus und LiveCircle zuständig. Der Coding Profi verwendet die normalen Chat- und autorisierten Host-Einstiege für Kommunikation und Projektzugriff.

## Verbundabnahme dieses Patches

Erwartete Kette: bestehender Code oder Neubau → Fachanalyse → autorisierte Änderung → Regression → Windows-Projektstarter → Abschlussaudit. Bei ausdrücklich beauftragtem Export folgen Paketierung und ZIP-Readback. Der zentrale Router, die Einstiege für Code-Erstellung und Review, die Patch-Übergabe, die Testfacette und der Engineering-Zyklus verweisen auf den gemeinsamen Abschluss. Eine statisch geprüfte Verweiskette ist ein eigener Nachweis. Praktische Facettenauswahl im frischen Plugin-Chat und Windows-Doppelklick benötigen jeweils eine reale Ausführung.

## Sprachabnahme

| Fall | Erwartung |
| --- | --- |
| Frischer Start ohne gespeicherte Auswahl, auch auf deutschem Windows | Das Tool startet in Englisch. |
| Wechsel auf Deutsch und zurück | Sichtbare Tool-Texte wechseln vollständig. Englische Starter-Texte bleiben gleich. |
| Bestehende gültige Nutzerwahl | Die ausdrücklich gewählte Sprache bleibt erhalten. |
| Unbekannte Sprache oder fehlender deutscher Eintrag | Englisch greift als Rückfall. Fehlende Übersetzungen erscheinen im Audit. |
| Vorhandene Batchdatei mit deutscher Auswahl oder Meldung | Eigene Texte werden im Repair ins Englische übertragen. Dieselben Zweige und Exitcodes bleiben prüfbar. |

## ToolStarter-Abnahme

Nutze [Integration und Abnahme](../skills/toolstarter-coding/references/integration.md) für die tatsächlich belegten Aktionen. Der ausgelieferte Standard enthält keine aktiven Projektwerkzeuge.

| Fall | Ergebnis |
| --- | --- |
| Windows-Projekt mit belegtem Einstieg | Ein dokumentierter Doppelklick-Einstieg öffnet den Starter. Das konkrete Profil enthält alle beauftragten Start-, Prüf- und Build-Befehle. |
| Kompatible Laufzeit und Pakete vorhanden | Prüfung verwendet die vorhandene Umgebung. Es erfolgt kein Installationsaufruf. |
| Fehlende oder inkompatible Voraussetzung | Diagnose meldet die Abweichung. Bei vereinbarter Reparatur prüft der Starter danach dieselbe Fähigkeit erneut. Prüfe einen frischen Shell-Aufruf nach Runtime-Installation. |
| Fehlender Entwicklungsinterpreter oder Offline-Fehler | Der Launcher beziehungsweise die Aktion meldet die konkrete Voraussetzung und gibt einen Fehlerstatus zurück. Abhängige Aktionen werden nicht gestartet. |
| Build bestellt | Prüfe die tatsächliche Ausgabe anhand des dokumentierten Pfades und der Paketproben. |

## Abnahme der Selbstheilung

| Ausgangslage | Beobachtbares Soll |
| --- | --- |
| Alle benötigten Module vorhanden | Vorprüfung besteht, kein Installationsaufruf, App startet einmal. |
| Deklariertes Modul fehlt in der Projekt-venv | Setup läuft einmal, dieselbe Vorprüfung besteht danach, App startet einmal. |
| Setup scheitert oder erneute Vorprüfung scheitert | Englische Meldung, Fehlercode, kein App- oder Build-Start. |
| Unbekannter Import, fehlende eigene Datei oder DLL-Fehler | Konkreter Befund. Keine spekulative Paketinstallation. |
| App scheitert nach bestandener Vorprüfung | App-Fehlercode bleibt erhalten. Kein nachträglicher Setup-Aufruf. |

Für eine reale Abnahme erfasse den verwendeten Interpreter und die beobachteten Rückgabecodes. Die ToolStarter-Modi `check` und `diagnose` lösen keine Downloads aus.

## Menüabnahme

| Fall | Soll |
| --- | --- |
| ZIP entpacken und STARTEN.bat öffnen | Ein dokumentierter Einstieg. Englisches Menü zeigt nur tatsächlich vorhandene Aktionen. |
| Start oder Build bei reparierbarer Abhängigkeit | Ein Setup-Versuch, erneute Prüfung, dann einmaliger Start oder Build. |
| Check, Diagnostics oder Exit | Keine Installation. Keine versehentliche Folgeaktion. |
| Aktion scheitert | Englischer Status und tatsächlicher Exitcode sichtbar. Menü bleibt bedienbar. Ein bestehender nichtinteraktiver Aufrufer erhält den Exitcode direkt. |
| Nicht angebotene Aktion oder abgebrochene Auswahl | Kein Start und keine Installation. |
| Bestehender CI- oder Skriptaufrufer | Aufrufpfad, Parameter und Exitcode bleiben kompatibel oder werden mit allen betroffenen Aufrufern gemeinsam angepasst. |

## Abnahme beider Windows-Artefakte

Für Portable und Installer verwende die getrennten Prüfungen aus den [Windows-Auslieferungsprofilen](windows-auslieferungsprofile.md). Prüfe die tatsächlich gebauten Artefakte, ihre Zusatztools und ihre dokumentierten Einstiege. Ein erfolgreicher Build ist ein eigener Nachweis. Offline-Start, Installation und Deinstallation sind erst nach Beobachtung auf der passenden Windows-Zielplattform bestanden.

## TS-01 und TS-02 im Zielhost

Prüfe vor Weitergabe Portable und Setup gegen die Artefaktliste des externen ToolStarter-Manifests. Wiederhole für TS-01 einen gemeinsamen Build A und einen Einzelbuild mit geänderter Nutzlast B unter demselben Ausgabestamm. Der Einzelbuild muss den bestehenden Satz unberührt lassen. Der anschließende gemeinsame Build B bindet beide Ausgaben an die neue Nutzlast.

Starte für TS-02 auf einem geeigneten Windows-Zielhost sowohl die entpackte EXE als auch die installierte Verknüpfung im Direct-Modus aus einem normalen Benutzerkontext ohne vom Build injizierte Runtime-Variablen oder PATH-Einträge. Führe eine Projektfunktion aus, die die gebündelte Runtime tatsächlich braucht. Protokolliere Einstieg, beobachtete Funktion und Ergebnis je Paketart.
