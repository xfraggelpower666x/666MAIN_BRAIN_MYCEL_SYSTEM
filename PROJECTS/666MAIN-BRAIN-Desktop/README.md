# 666 MAIN BRAIN · PSYLLO Desktop

Native Windows-Oberfläche für den aktuellen MAIN-BRAIN-Checkout. Herausgeber
**666SOUNDsDESIGn · FRAGGLEPOWER666**.

## Start

1. Das MAIN-BRAIN-Repository mit dem Branch `666MAIN_BRAIN` auschecken.
2. Unter Windows `PROJECTS\666MAIN-BRAIN-Desktop\STARTEN.bat` doppelklicken.
3. Im Bereich **Current** den lokalen Stand lesen oder ausdrücklich mit GitHub
   abgleichen. **Checkpoint**, **Laufbelege** und **Workbench** nutzen die
   vorhandenen PSYLLO-Programme aus demselben App-Checkout.

Voraussetzungen: Windows, Python 3.10 oder höher mit Tkinter und Git im PATH.
Das Projekt verwendet die Standardbibliothek. Der Launcher kann alternativ
mit `STARTEN.bat --check` den lokalen Current und die Integrationspfade auslesen.
Die Protokolldatei `.666mainbrain/desktop.log` im Benutzerprofil enthält
Zeit, Aktion und Ergebnisstatus. 

| Bereich | Daten und Ergebnis |
| --- | --- |
| Current | Git-HEAD, Pointer-Blob aus diesem Commit und Arbeitsbaum. Der GitHub-Abgleich liest den öffentlichen Branch-HEAD separat und aktualisiert keine lokalen Refs. |
| Checkpoint | Checkpoint und unabhängige Projektbindung als JSON plus das zu prüfende lokale Git-Projekt. |
| Laufbelege | Soll-Vertrag, Receipt und Artefaktordner. Ausgabe des vorhandenen Belegprüfers. |
| Workbench | Projekt-Datensatz und optionaler UI-Handoff. Speichert eine HTML-Datei am gewählten Pfad. |

Die App delegiert an den bestehenden Coding-Prüfstand. SYSTEMSTART und UPDATE
bleiben die nativen Chat-/Repo-Abläufe. Die App führt lokale Diagnosen aus und
exportiert die Workbench. Die Windows-Abnahme umfasst Doppelklick, Auswahl der
Eingabedateien, Anzeige eines Befunds und Workbench-Export.
