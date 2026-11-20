# Gemeinsames 666CLS-Archiv

666CLS stellt vier Archivbereiche für mehrere Frameworks bereit. Jedes Framework verwendet eine eigene Kennung und verwaltet seinen eigenen Start, Zustand und Arbeitsablauf. Zugriff ist pro Framework und Archivbereich konfigurierbar.

| Aktion | Sichtbarkeit und Wirkung |
|---|---|
| `read` | Liest veröffentlichte Einträge eines erlaubten Bereichs aus dem verifizierten 666CLS-Pointer. |
| `submit` | Legt einen Eintrag mit eigener Einreichungs-ID in die private Inbox. Eine identische Wiederholung gibt dieselbe Quittung zurück. |
| `pending` | Zeigt der 666CLS-Prüfinstanz noch nicht im aktiven Archiv enthaltene Einreichungen. |
| `prepare` | Erstellt aus ausgewählten Quittungen und dem aktuellen Bestand einen vollständigen Update-Kandidaten. |
| `666CLS UPDATE` | Übernimmt nach Prüfung den vorbereiteten Kandidaten über den bestehenden Release-Ablauf. |

## Einrichtung auf einem gemeinsamen Host

Einen privaten, zugriffsgeschützten Ordner außerhalb des gesamten Git-Checkouts anlegen. Das Python-Programm benötigt den geprüften 666CLS-Checkout. Die SQLite-Inbox liegt auf einem **lokalen Datenträger** dieses Hosts. Die Framework-Anbindung ruft die CLI über den Betreiber oder einen vertrauenswürdigen Prozess auf. Mehrere Aufrufe dürfen parallel erfolgen. Ein verteilter HTTP-Dienst und Chat-Connectoren sind separate Anbindungen.

In den privaten Ordner kommt `clients.json`, wie unten gezeigt. `token_sha256` enthält jeweils den SHA-256-Hash eines eigenen zufällig erzeugten Tokens mit mindestens 32 Zeichen. Der Aufrufer übergibt das Token ausschließlich in `CLS_ARCHIVE_TOKEN`. Ein Framework bekommt keinen direkten Dateizugriff auf die Namen/Token anderer Clients, die Inbox oder den GitHub-Schreibzugang. Der Host-Betreiber setzt die Dateisystemrechte durch.

```json
{
  "system_id": "666CLS-CORE-001",
  "clients": {
    "framework-a": {
      "token_sha256": "SHA-256 des Tokens von Framework A",
      "read": ["LYRICS", "STORIES"],
      "submit": ["LYRICS"]
    },
    "framework-b": {
      "token_sha256": "SHA-256 des Tokens von Framework B",
      "read": ["LYRICS", "STORIES"],
      "submit": ["STORIES"]
    },
    "cls-review": {
      "token_sha256": "SHA-256 des Tokens der 666CLS-Prüfinstanz",
      "review": true
    }
  }
}
```

## Aufrufe

Vom 666CLS-Projektordner aus. In den Beispielen steht `C:/666CLS-Private` für den privaten Ordner. Pro Aufruf ist das passende Token in der Prozessumgebung gesetzt.

```text
python runtime/shared_archive.py --private-dir C:/666CLS-Private --client framework-a read LYRICS
python runtime/shared_archive.py --private-dir C:/666CLS-Private --client framework-a submit LYRICS song-001 C:/666CLS-Private/song.json
python runtime/shared_archive.py --private-dir C:/666CLS-Private --client cls-review pending
python runtime/shared_archive.py --private-dir C:/666CLS-Private --client cls-review prepare 1.24.3 C:/666CLS-Private/candidate.json framework-a/song-001
```

Die Eingabedatei verwendet einen einzelnen 666CLS-Datensatz, z. B. `{"title":"Titel","source_text":"Originaltext"}`. Die Entscheidung über den Bereich bleibt Aufgabe der Fachprüfung. 666CLS ergänzt eine neue Archiv-ID, die Framework-Kennung und die Einreichungs-ID. Falls die Quelle schon eine ID hat, bleibt sie als Provenienz erhalten.

Bei erkennbaren Zugangsdaten verbleibt die unveränderte Einreichung privat in der Inbox. Liste und Oberfläche zeigen `HOLD / SOURCE_VAULT_ONLY` mit der Quittung. Der Kandidatenbau blockiert diese Einreichung. Die automatische Erkennung deckt bekannte Muster ab. Die Freigabeprüfinstanz beurteilt zusätzlich Quelle, Inhalt und Veröffentlichungsrechte.

Nach der Freigabe durch die 666CLS-Prüfinstanz kann der bestehende `666CLS UPDATE`-Ablauf angewendet werden. Da der konfigurierte GitHub-Zweig öffentlich ist, gehören in veröffentlichte Releases ausschließlich öffentlich freigegebene Inhalte. Einreichungen, privat erzeugte Kandidaten und deren Backups bleiben im geschützten Arbeitsbereich.

## Prüfen

```text
python -m unittest discover -s tests -v
```

## Intelligente Menüführung

Das bestehende Archiv-Dashboard enthält die Bereiche **Archiv**, **Eingang**, **Frameworks** und **Nachweise**. Eingaben wie „Einreichung“, „Framework-Zugriff“ und „Prüfsumme“ führen zur passenden Ansicht. Der nächste Schritt wird pro Ansicht aus dem erfassten Stand abgeleitet. Die einfache Ansicht aus `666CLS SYSTEMSTART --dashboard` markiert die Inbox als offen.

Für den Prüfzugang gibt es dieselbe Ansicht mit geprüften Inbox-Zählern. Sie zeigt nur Summen pro Bereich und keine privaten Texte oder Quittungen. Eine neue Datei erzeugt einen neuen Snapshot. Die HTML-Datei löst keine Freigaben oder Schreibvorgänge aus.

```text
python runtime/shared_archive.py --private-dir C:/666CLS-Private --client cls-review dashboard C:/666CLS-Private/review.html
```

Ein optionaler `--checkpoint` übernimmt die Ansicht bei gleicher System-ID und Release-Revision. Ein alter Handoff lässt sich durch Weglassen der Option überspringen. Null offene Einreichungen und eine ungeprüfte Inbox sind unterschiedliche Zustände.

## Das Archiv und Frameworks im selben Menü steuern

Das private Bedienmenü startet auf dem Rechner, der den geprüften 666CLS-Checkout und die Inbox hält. Starte mit dem Token der Prüfrolle in `CLS_ARCHIVE_TOKEN` und öffne die im Terminal ausgegebene lokale Adresse. Die Adresse gilt für diesen Prozess. Beende die Sitzung mit Strg+C.

```text
python runtime/archive_console.py --private-dir C:/666CLS-Private --operator cls-review
```

Im privaten Ordner definiert `frameworks.json` die vom Betreiber geprüften Frameworks. Die Schlüssel müssen vorhandenen Archivprofilen aus `clients.json` entsprechen. Die unten stehenden Namen sind Platzhalter. Speichere für jedes echte Framework die geprüfte Quelle, Revision und seine tatsächlich unterstützten Start- oder Fortsetzungsaktionen. Die Konsole prüft das Konfigurationsformat beim Laden. Der Betreiber gleicht externe Quellen und Revisionen bei jeder Änderung des Eintrags ab.

```json
{
  "frameworks": {
    "framework-a": {
      "name": "Name des Frameworks",
      "authority": "Belegter Repo-Pfad",
      "revision": "Geprüfte Revision",
      "actions": {
        "start": {"mode": "chat", "trigger": "Belegter nativer Starttrigger"},
        "resume": {"mode": "local", "trigger": "Belegter nativer Fortsetzungstrigger",
                   "argv": ["C:/Pfad/zum/Interpreter.exe", "C:/Pfad/zum/Adapter.py", "Fester Parameter"],
                   "cwd": "C:/Pfad/zum/Framework"}
      }
    }
  }
}
```

`chat` liefert den nativen Trigger zum Kopieren in den zugehörigen Chat. `local` führt den vom Betreiber eingetragenen Adapter mit festen Argumenten aus. Verwende für lokale Aktionen ausschließlich vertrauenswürdige Adapter. Framework-Steuerung enthält Start und Fortsetzung. Das Archivmenü zeigt die erlaubten Bereiche des gewählten Frameworks, lädt Einträge und legt neue Texte im gemeinsamen Eingang ab. Jeder geladene Eintrag zeigt die gespeicherte Datenbank-ID. Die Suche filtert innerhalb des gerade geladenen Archivbereichs nach Titel oder ID. Die Ablage zeigt eine Quittung und erfasst die Prüfrolle, die im Namen des Frameworks handelt.

Im Eingang öffnet der Betreiber einzelne Einreichungen, wählt sie aus und speichert einen privaten Kandidaten. Die Veröffentlichung erfolgt im 666CLS-Update-Ablauf. „Nachweise und Visualisierung“ zeigt den geprüften Release und die aktuellen Inbox-Summen je Bereich. Die Übersicht lässt Inhalte und Quittungen privat im Eingang.

## Eingefügte Einzelsysteme einordnen

Im Menü **Systemaufnahme** ein JSON-Dossier laden oder einfügen. Beim Einfügen eines vorhandenen Frameworks werden zuerst Zweck, Authority, Startweg, Zustand und Abhängigkeiten aus seinen nativen Quellen ermittelt. Im Dossier bekommt jeder Befund eine Fundstelle und die Revision des aufgenommenen Systems. Ein Vergleich bezieht sich auf eine registrierte Zielrevision. Die UI ordnet die eingetragenen Befunde regelbasiert ein. Fundstellen und Revisionen werden als Prüfbasis angezeigt. Ihre fachliche Prüfung findet beim Erstellen des Dossiers statt.

```json
{
  "name": "Beispielsystem",
  "revision": "source-r3",
  "target": "framework-a",
  "target_revision": "target-r2",
  "facts": {
    "native_authority": {"value": true, "source": "AUTHORITY.md, Abschnitt 1", "revision": "source-r3"},
    "native_entry": {"value": true, "source": "START.md, Startkommando", "revision": "source-r3"},
    "shared_component": {"value": true, "source": "Vergleich der Archiv-Schnittstellen r3 ↔ r2",
      "revision": "source-r3", "target_revision": "target-r2"}
  }
}
```

Die Entscheidschlüssel im Dossier sind `native_authority`, `native_entry`, `own_state`, `host_dependency`, `same_purpose`, `same_scope`, `compatible_lifecycle`, `compatible_state`, `continuity_preserved` und `shared_component`. Ein negatives Ergebnis muss ebenso belegt werden wie ein positives. Unbekannte Befunde werden weggelassen.

Ein eigener Einstieg oder Zustand zusammen mit eigener Zuständigkeit stützt ein eigenständiges Framework. Ein belegter gemeinsamer Baustein kann trotzdem geteilt werden. Ein abhängiger Baustein ohne eigene Zuständigkeit, eigenen Einstieg und eigenen Zustand kommt als Modul infrage. Konsolidierung setzt denselben Zweck und Zuständigkeitsbereich, kompatiblen Betrieb und Zustand sowie nachgewiesene Kontinuität voraus. Eine Empfehlung ändert Registry, Dateien, Trigger und Archive erst über den zuständigen Freigabepfad. Rohdateien oder Text-Exporte können zur Dossiererstellung geprüft werden. Die UI übernimmt dafür aktuell strukturierte JSON-Dossiers.

Bei den Paketrollen kennzeichnet `package_only` einen reinen Datenstand, Output oder Beleg. `native_child` und `native_addon` erfordern einen nativen Vertrag als Fundstelle und die belegte Zielkennung im Feld `parent`. Die Parent-Angabe aus einem Dossier ist Provenienz. Sie führt zu keiner Registrierung oder Aktivierung. `inverse_contract` vergleicht die Ein- und Ausgaberichtung mit einer konkreten registrierten Zielrevision. Gegensätzliche Transformationsrichtungen bleiben getrennt. Wenn das Dossier zugleich eine vollständige Konsolidierungsverträglichkeit behauptet, fordert die Prüfung eine Auflösung des Widerspruchs.
