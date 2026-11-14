# Peer-Tool-Intake · Freeze-ZIP-Host-Gegenprobe

## Basis und Recovery

Branch `666MAIN_BRAIN`, Ausgangscommit `7d057aa23981ea931a3dee32ab4408e8f211d442`. Die Preimages sind über diesen Commit wiederherstellbar.

| Datei | Git-Blob vor Änderung |
| --- | --- |
| `CURRENT_POINTER.md` | `838bf267c0cc2a4d97f620373473a5d0bd0ee59e` |
| `INTEGRATIONS/PLUGIN_CAPABILITIES/WORKFLOWS_R01.md` | `9a293a0f885af50eea47b9b04935694ba79862dd` |
| `HOST/FRESH_CHAT_ACCEPTANCE_MATRIX.md` | `d7720fc7babb4ad05183b2c419cc31da8c602b6b` |

## Nachweis aus dem bereitgestellten Testchat

Der Erstaufruf wählte `INTEGRATIONS/CODEFORGE/verify_freeze.py`. Die ausgegebene Klasse `REUSE_EXISTING / NO_NEW_TOOL` entsprach fachlich der Wiederverwendung und wich vom kanonischen Klassenwert ab. Der Beleg für den gelesenen Entscheidungsvertrag fehlte im Erstbericht.

Die gezielte Nachfrage im selben Chat lieferte `REJECT_DUPLICATE` und den Vertrags-Blob `4efc4f59bd0a2eb6f29cba2ef868190a14e4240c`. Vertrags-Blob und Klasse wurden unabhängig auf GitHub am Ausgangscommit bestätigt. Der Host-Nachweis stammt aus den bereitgestellten Antworten. Eine Release-ID wurde im Testchat nicht ausgewiesen. Das Ergebnis verifiziert diesen Fall nach Nachfrage. Die automatische Klassenausgabe im ersten Turn bleibt offen.

## Abnahme des Workflow-Deltas

Der Workflow fordert jetzt den direkten Readback des Entscheidungsvertrags und dessen exakte Klasse bereits beim ersten Ergebnis. Bei fehlender Vertragsquelle bleibt die Klassifizierung offen. Prüfe in einem frischen Plugin-Chat erneut denselben Freeze-ZIP-Vorschlag ohne Angabe der Sollklasse. Erwartet werden `REJECT_DUPLICATE`, der bestehende Prüferpfad, der gebundene Commit und der Vertrags-Blob im ersten Ergebnis. Diese Gegenprobe für den geänderten Workflow steht aus.
