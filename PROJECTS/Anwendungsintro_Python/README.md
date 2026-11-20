# Anwendungsintro für Python/Tkinter

Das Modul enthält einen neutralen Startbildschirm mit konfigurierbaren Texten, Farben, Bildern und Startphasen. Es benötigt Python 3.10 oder neuer mit Tkinter. Für das Modul sind keine zusätzlichen Python-Pakete erforderlich.

## Demo starten

```sh
python demo.py
```

## In eine Tkinter-Anwendung einbauen

1. `app_intro.py` neben deine Startdatei kopieren.
2. Nach `root = tk.Tk()` das Hauptfenster mit `root.withdraw()` ausblenden.
3. Vor `root.mainloop()` das Intro erzeugen. Im Callback das Hauptfenster mit `root.deiconify()` anzeigen, sobald das Intro `IntroResult.READY` meldet. `demo.py` enthält das vollständige Beispiel.
4. Optional `title`, `version`, `subtitle`, `theme`, `phases`, `logo` und `banner` konfigurieren. Für Bilder empfiehlt sich PNG. Pfade relativ zur Startdatei lassen sich mit `Path(__file__).resolve().parent / "logo.png"` bilden.

Ein `Phase`-Eintrag enthält Titel, Detailtext, Fortschritt (0–99) und Dauer in Millisekunden. Die Fortschrittswerte beschreiben die Anzeigeschritte. Der Wert 100 erscheint erst bei der Übergabe. Mit `phases=()` kannst du die zeitgesteuerten Phasen auslassen.

## Auf die tatsächliche Initialisierung warten

Übergib `ready=threading.Event()` an `IntroWindow` und setze dieses Event nach erfolgreicher Initialisierung. Ein Worker darf das Event setzen. Tkinter-Aufrufe bleiben im GUI-Hauptthread. Lange Initialisierungen dürfen die GUI-Ereignisschleife nicht blockieren. Bei einem Startfehler sollte die Anwendung das Intro im GUI-Thread mit `cancel()` schließen und ihren eigenen Fehlerdialog verwenden.

Nach dem letzten Anzeigeschritt wartet das Intro bis zu `timeout_ms` auf das Signal. `None` lässt es unbegrenzt warten. Der Callback erhält genau einen der folgenden Werte.

| Ergebnis | Wann es auftritt |
| --- | --- |
| `IntroResult.READY` | Alle Phasen sind durchlaufen und ein optionales Startsignal liegt vor. |
| `IntroResult.TIMED_OUT` | Das Startsignal fehlt nach Ablauf der Wartezeit. |
| `IntroResult.CANCELLED` | Das Intro wird über Escape, das Fensterschließen oder `cancel()` beendet. |

Wird die gesamte Anwendung geschlossen und das Hauptfenster zerstört, werden die Timer des Intros ebenfalls beendet.

## Andere Desktop-Frameworks

Dieses Modul ist an Tkinter gebunden. Für PySide/PyQt, Electron oder .NET muss die Oberfläche samt Timer und Übergabe an das Hauptfenster über das jeweilige Framework eingebunden werden. Titel, Phasen, Farben und der Ablauf sind dabei übertragbar.

## Prüfungen

`python -m unittest -v` prüft Phasenübergabe, Bereitschaftssignal, Zeitüberschreitung, Abbruch und Konfigurationsvalidierung. Die Tests nutzen Tcl-Timer, ersetzen aber die grafischen Widgets. Der Start auf einem Windows-Desktop lässt sich mit `python demo.py` prüfen.
