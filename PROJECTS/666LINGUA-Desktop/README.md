# 666LINGUA Desktop 1.8.0

## Windows starten

Wähle das ZIP für deinen PC: `666LINGUA-Windows-x64.zip` für Intel/AMD oder `666LINGUA-Windows-ARM64.zip` für Windows auf ARM. Entpacke das ganze ZIP, damit die Electron-Laufzeitdatei beim Start neben der EXE liegt.

- **Installieren:** Starte `666LINGUA-Setup-x64.exe` bzw. `666LINGUA-Setup-ARM64.exe`. Du kannst das Ziel eingeben oder im Ordnerdialog auswählen. Der Standard ist `%LOCALAPPDATA%\Programs\666LINGUA`. Startmenü, Desktop-Verknüpfung und anschließender Start sind einzeln wählbar. Windows bietet die Deinstallation in den Einstellungen an.
- **Direkt starten:** Öffne `666LINGUA-x64.exe` bzw. `666LINGUA-ARM64.exe`. Beim ersten Start entpackt die App die mitgelieferte Electron-Laufzeit in den lokalen Benutzer-Cache. Weitere Starts verwenden die bereits entpackte Version.

Das App-Fenster läuft mit der mitgelieferten **Electron-Version 45.3.2**. Die normale App-Nutzung und das Setup funktionieren offline. Der Go-Übersetzungskern tauscht Daten per Prozesspipe mit Electron aus. Go wird nur zum Entwickeln und Bauen benötigt. Die 666LINGUA-EXEs sind nicht signiert.

## Startintro

Vor der Arbeitsfläche erscheint das 666LINGUA-Intro mit dem mitgelieferten Platinenhintergrund und dem transparenten Logo. Der Ablauf orientiert sich an der Vorlage `PROJECTS/Anwendungsintro_Python`: Die vier Boot-Stufen **666LINGUA BOOTING**, **GERMAN INJECTED**, **AMERICA INJECTED** und **SEMANTIC BOOST** laufen über rund sieben Sekunden. **666LINGUA READY** erscheint bei tatsächlicher Bereitschaft und bleibt 2,5 Sekunden sichtbar, bevor die Arbeitsfläche übernimmt. Für die Desktop-App ist er in der bestehenden lokalen Oberfläche eingebaut. Über **Intro überspringen** oder **Esc** kannst du sofort weiter. Die Bilder sind in der App enthalten.

## Vollbild-Arbeitsfläche

Die Hauptansicht hält Quelltext und Hauptübersetzung in derselben Ansicht. Lange Texte scrollen im jeweiligen Textfeld. Bei geringer Fensterhöhe lassen sich die Bereiche intern scrollen.

**Wörterbücher**, **Lernen**, **Zeit umrechnen**, **Systemnachweis**, **Entscheidung & Belege** und **Weitere Fassungen** öffnen als Overlays in demselben App-Fenster. Schließe ein Overlay über **Schließen**. Mit **Esc** schließt du das aktive Overlay. Das Belegfenster öffnet auf Klick, während der Status am Knopf anzeigt, ob die Ausgabe blockiert ist.

## Übersetzen

- Die Oberfläche startet auf Englisch. Der Umschalter ENG/DEU speichert die App-Sprache sofort lokal. Die Übersetzungsrichtung wird separat gespeichert. Standard ist Englisch → Deutsch. Verfügbar sind Deutsch, Englisch (international, USA, Vereinigtes Königreich), Spanisch und brasilianisches Portugiesisch.
- Der lokale Übersetzungskern kombiniert belegte Satz- und Phrasentreffer. Der Systemnachweis nennt Quelle, Abschnitt und Entscheidungsgrund. Vollständig unbekannte oder mehrdeutige Abschnitte sperren die vollständige Ausgabe. Eine bestätigte eigene Zielfassung kann den fehlenden Treffer ergänzen.
- Die Hauptübersetzung steht im rechten Textfeld. Die natürlichen, präzisen, emotionalen und spielerischen Varianten stehen unter **Weitere Fassungen**. Wo keine eigenständige Wortfassung belegt ist, zeigt die App die Hauptfassung mit einem entsprechenden Hinweis.
- Semantische Emojis verstärken geeignete Aussagen im Text. Der technische Kanal erhält keine automatisch hinzugefügten Emojis. Bei identischen Symbolen innerhalb eines Texts wird die vorgeschlagene Verstärkung nur einmal gesetzt. Bereits eingegebene Emojis können erhalten bleiben.
- Der Force Lock verwendet ausschließlich den lokalen Kern. Der Entwicklungsmodus `--serve` bindet an einen zufälligen Loopback-Port. Das Desktop-Fenster verwendet den Prozesskanal. Die Oberfläche verwendet keine remote geladenen Assets oder Übersetzungsdienste.
- Der letzte übersetzte Quelltext kann aus demselben Fenster wieder eingesetzt werden. Ein Neustart verwirft ihn.
- Texte werden standardmäßig nicht aufgezeichnet. Explizit bestätigte Übersetzungsregeln liegen in `%APPDATA%\666SOUNDsDESIGn\666LINGUA\translations` und können im Bereich **Lernen** geprüft, bearbeitet und gelöscht werden. Beim Ersetzen verhindert ein Abgleich mit der gelesenen Revision, dass eine dazwischen bestätigte Fassung still überschrieben wird. Deinstallation erhält diese Regeln.

Der Kern arbeitet mit einem begrenzten Phrasenbestand, einem Uhrzeit-Satzmuster, 30 übernommenen direkten Profilfällen und bestätigten eigenen Fassungen. Freitext außerhalb dieser Abdeckung bleibt offen. Die Quellenarchive dokumentieren weitere KI-Host-Konzepte. Der Windows-Ableger führt daraus keine Chat-Engine aus.

## Kontext und bestätigte Formulierungen

- Bei hinterlegten Mehrdeutigkeiten prüft die App die direkt angrenzenden Sätze in derselben Zeile. `Buenas noches. ¿Cómo estás?` ergibt `Guten Abend. Wie geht es dir?`. `Buenas noches. Duerme bien.` ergibt `Gute Nacht. Schlaf gut.`. Ohne passenden Hinweis oder bei widersprüchlichen Hinweisen erscheinen die Lesarten im Belegfenster und die Gesamtausgabe bleibt offen.
- Unter **Belege** zeigt die App den verwendeten Quellabschnitt, den Kontextbeleg, die geprüften Lesarten und den gewählten Text. Regeln können in `semantic.go` nachvollzogen werden.
- Bestätigte Korrekturen für eine Satzfolge sind im gleichen Sprachpaar in längeren Texten wiederverwendbar. Dazu muss die normalisierte Satzfolge vollständig passen und darf keinen neuen Absatz überspringen. Ein innerer Teiltreffer ist auf acht Sätze begrenzt. Kreuzen sich zwei bestätigte Folgen oder weichen eine gespeicherte Einzelfassung und der belegte Satzkontext voneinander ab, verlangt die App eine gemeinsame Fassung. Das Löschen einer Bestätigung entfernt ihre Wirkung beim nächsten Übersetzen.
- Zahlen, Links und Kennungen bleiben überprüfbar. Die Übersetzung prüft diese pro Abschnitt und für die gesamte Hauptfassung. Stilfassungen, die geschützte Inhalte ändern würden, fallen auf die Hauptfassung zurück.

Die Kontextregeln decken die dokumentierten Lesarten ab. Unbekannte Kontexte und nicht erfasste Freitexte bleiben offen.

## Kopieren, Teilen und eigene Wörterbücher

- **Quelltext kopieren** übernimmt das gesamte Eingabefeld. **Übersetzung kopieren** übernimmt die sichtbare Hauptfassung. Alternative Fassungen haben ihre eigenen Kopierbuttons.
- **Teilen** steht unmittelbar neben **Kopieren**. Es übergibt nur den gewählten Quell- oder Zieltext. **WhatsApp** übergibt den vorbereiteten Text an die installierte WhatsApp-App, sofern sie unter Windows als Protokollhandler verfügbar ist. Ist sie nicht verfügbar, kannst du den Text kopieren. **E-Mail** öffnet einen Entwurf im Standard-Mailprogramm. **Weitere Apps** erscheint, wenn die verwendete Oberfläche die Systemfreigabe für Text anbietet. Empfänger und Versand wählst du im Zielprogramm. Bei zu langen Freigabelinks kannst du den vollständigen Text kopieren oder die Systemfreigabe nutzen.
- Unter **Wörterbücher** gibt es getrennte Einträge für **Deutsch → Englisch** und **Englisch → Deutsch**. Gib Quellbegriff und Zielbegriff ein und speichere sie. Die Suche findet beide Seiten. Zum Ändern der Übersetzung nutze **Bearbeiten**. Namen können mit identischer Schreibung gespeichert werden.
- Beim Übersetzen greift der Kern auf das Wörterbuch der gewählten Richtung zurück. Er verwendet exakte Begriffe, unterstützte Satzmuster und eindeutige Wortzuordnungen in hinterlegten Satzübersetzungen. Die englischen Varianten teilen sich pro Richtung ein Wörterbuch. Bestätigte vollständige Übersetzungen haben weiterhin Vorrang.
- Beispiel für **Deutsch → Englisch**. Speichere `Neonspule` als `a neon coil`. Die Eingabe `Ich brauche Neonspule.` wird zu `I need a neon coil.`. Der Beleg nennt den verwendeten Eintrag. Gewünschte Artikel kannst du mit dem Zielbegriff speichern. Unbekannte Satzstrukturen bleiben offen.
- Die Einträge liegen lokal in `%APPDATA%\666SOUNDsDESIGn\666LINGUA\dictionaries`.

## Benutzerprofil, Uhren und Emojis

- Über **Profile / Profil** registrierst du Name, Geburtsdatum und Wohnort auf diesem PC. Das westliche Sternzeichen ergibt sich aus dem Datum. Das Offline-Ortsverzeichnis schlägt die IANA-Zeitzone vor. Bei Mehrdeutigkeit wähle den konkreten Ort oder die Zeitzone. Kleine oder unbekannte Orte lassen sich mit einer manuell gewählten Zone speichern.
- Ein fester Gesprächspartner ist optional. Seine Sprache und Zeitzone werden bei der Einrichtung als Ziel übernommen. Änderungen der Übersetzungsrichtung und der Zielzeitzone werden separat gespeichert, solange du keine andere Voreinstellung im Partnerprofil setzt.
- Oben mittig zeigt die App deine Ortszeit und das Kalenderdatum. Ohne Profil nutzt sie die Zeitzone des Geräts. Über der Ausgabe erscheinen Zielsprache, Zielzeitzone, Uhrzeit, Datum, UTC-Offset und Kalendertagversatz. Bei offener Zielzeitzone bleibt die Zieldatumsanzeige leer.
- **Time conversion / Zeit umrechnen** rechnet ein ausdrücklich gewähltes lokales Datum und eine Uhrzeit zwischen beiden IANA-Zonen um. Zeitlücken und doppelte Stunden beim Sommerzeitwechsel werden angezeigt. Eine Zeitangabe im Quelltext löst einen Hinweis aus. Für die automatische Umdeutung relativer Angaben im Freitext fehlen noch belastbare Kontextdaten.
- **Insert emoji / Emoji einfügen** öffnet das Offline-Verzeichnis mit 3.998 Sequenzen, Suchfunktion und Kategorien. Die Auswahl setzt das Emoji an der Cursorposition ein oder ersetzt die markierte Stelle. Semantische Emoji-Verstärkung lässt sich separat schalten.
- Name, Geburtsdatum, Sternzeichen, Wohnort, Zeitzone, optionaler Partner und Einstellungen liegen in `%APPDATA%\666SOUNDsDESIGn\666LINGUA\desktop-settings.json`. Das Profil kann in der App gelöscht werden. Die Oberfläche benötigt dafür kein Online-Konto.

Die Windows-App startet im Vollbild. **Full screen / Vollbild** wechselt zwischen Vollbild und Fenstermodus. Menüpunkt **2** startet direkt im Fenstermodus. Details zum Vergleich mit dem direkt gelesenen Live-Stand stehen in [LIVE-ABGLEICH.md](LIVE-ABGLEICH.md).

## Bauen und prüfen

`STARTEN.bat` ist der einzige Batch-Einstieg. Der Starter prüft die Mindestversion aus `go.mod` (derzeit Go 1.25), die tatsächliche Version und den Compiler. Er verwendet eine funktionierende Installation aus dem Suchpfad, den üblichen Windows-Ordnern oder dem lokalen Projektcache.

Fehlt eine passende Toolchain, laden Setup, Build, Paketierung, Tests, Reparatur und Komplettlauf ein passendes stabiles Go-Archiv für Windows x64 oder ARM64 von `go.dev`. Der Starter prüft SHA-256, richtet Go in `.toolchain/go` ein und setzt die gewählte Aktion nach der erneuten Compilerprüfung fort. Dafür braucht der erste Download Internet und der Projektordner Schreibrechte. Die lokale Installation benötigt keine Administratorrechte und verändert den systemweiten PATH nicht. Diagnose, Projektcheck und normaler EXE-Start laden keine Tools herunter. Windows-Builds laden bei Bedarf die festgelegten offiziellen Electron-Archive herunter und prüfen SHA-256. Die Archive bleiben in `build-output/electron-downloads`. Über `LINGUA_ELECTRON_ARCHIVES` kann ein vorhandener Archivordner verwendet werden. Ohne Argumente zeigt die Batch das Menü und kehrt nach einer Aktion dorthin zurück. Für Skripte akzeptiert sie Langoptionen und Kurzformen, z. B. `STARTEN.bat installer /nopause`. `/nopause` verhindert die Fehlerpause und lässt den Exitcode erhalten.

| Aktion | Ergebnis |
| --- | --- |
| `--start` | App-Fenster. Nutzt `release`, oder einen Einzelbuild, wenn keine Release-EXE vorhanden ist. |
| `--windowed` | Öffnet das eigene App-Fenster im Fenstermodus. `--browser` ist als alter Befehlsalias verfügbar. |
| `--diagnose` | Vergleicht Quellarchiv-Hashes, Release-Hashes, PE-Architektur und Portable-Inhalt. |
| `--repair` | Prüft die Quellen, führt Tests aus, erzeugt ein vollständiges Release und sichert die alte Ausgabe separat. |
| `--dev` / Menüpunkt **5** | Baut die EXE für diesen PC in `build-output/dev`, stellt die zugehörige Electron-Laufzeit bereit und startet den Entwicklungsbuild direkt. |
| `--build` | Kompiliert beide Programm-EXEs und legt die Electron-Archive in `build-output/build` daneben. |
| `--test` | Startet Entwickler- und Regressionstests. |
| `--check` / `check` | Prüft vorhandenes Go, die Projektdateien und führt die Tests aus. |
| `--package` / `portable` | Testet und baut ein portables ZIP pro Architektur in `build-output/package`. |
| `--toolstarter` | Prüft die Projektstruktur sowie die beiden R19-Quellarchive bei vorhandenem Quellenordner. |
| `--setup` / `installer` | Testet und baut beide Windows-ZIPs mit Setup und direkt startbarer App in `build-output/setup`. |
| `--all` | Testet und erzeugt die vollständigen Windows-Pakete für x64 und ARM64 samt Prüfliste in `release`. |

Das Toolstarter-ZIP lag den 666LINGUA-Anhängen nicht bei. Das Batch-Muster aus dem Auftrag dient als Vorlage für Projektcheck, Menü und CLI. Der Projektcheck läuft im Build-Werkzeug und ist kein Bestandteil der Anwendung.

Auf Linux können die beiden Windows-Architekturen mit `go run -buildvcs=false ./cmd/build all` gebaut werden. Quellarchive und nachvollziehbare Übernahmen stehen in [QUELLEN.md](QUELLEN.md).

## Öffentlicher Projekt-Checkout

Die unveröffentlichten nativen R19-Archive und ihre Begleitdateien liegen in früher übergebenen Gesamtpaketen. Der öffentliche Checkout enthält die abgeleiteten Desktop-Testfälle und Ressourcen. Fehlt der Ordner `sources`, meldet die Build-Prüfung den fehlenden Archivbeleg und kann mit den Desktop-Dateien fortfahren. Bei vorhandenem Ordner werden beide Originalarchive vollständig gegen ihre SHA-256-Werte geprüft.
