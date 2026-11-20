# 666TDH Begleit-Daemon — repo-native zentrale Lesebefehle R3

SYSTEM_ID=666TRACKHUB-001
OWNER=666TDH
DIRECT_USER_TRIGGER_ONLY=TRUE
DAEMON_ROUTE_AUTHORITY=NONE
DAEMON_WRITE_AUTHORITY=NONE
DAEMON_UPDATE_AUTHORITY=NONE
DAEMON_DECISION_AUTHORITY=NONE
DAEMON_AUTOACTIVE_ADVISORY=TRUE
NO_SECOND_ROUTER=TRUE
NO_FOREIGN_AUTOACTIVATION=TRUE

## Ausführbare direkte Befehle

Die folgenden bereits historisch dokumentierten Daemon-Befehle werden ausschließlich
über den nativen `tdh.py`-Root-Parser zugelassen. Registrierungsquelle:
`runtime/TRIGGERS.json` Feld `daemon`; es gibt keine zweite Parserinstanz.

- `666TDH DAEMON STATUS` → Hub-Current und Begleitstatus lesend anzeigen
- `666TDH DAEMON NEXT` → beleggebundene nächste sichere Aktion anzeigen
- `666TDH DAEMON MENU` → erlaubte Daemon-Befehle anzeigen
- `666TDH DAEMON CONTINUE` → nur Hub-Continuity prüfen, ohne Child zu wählen
- `666TDH DAEMON BACK` → Root-Übersicht ohne Mutation
- `666TDH DAEMON HELP` → Begleitvertrag und zulässige Befehle anzeigen
- `666TDH DAEMON STOP` → Ausgabe im laufenden CLI-Aufruf markieren, KEIN globaler
  oder persistenter Stop. Die lokale HTML-UI kann die Daemon-Karte ausblenden.
- `666TDH DAEMON WEITER` → lesende Hub-Continuity
- `666TDH DAEMON NEW CHAT` → nichtautoritatives Root-Checkpoint-Template

Aussagen über dauerhaft aktive Hintergrundprozesse, autonome Musikentscheidungen,
unsichtbare Speicherungen oder Chat-Host-Persistenz sind verboten.
Der Daemon darf keine Childs auswählen, keinen fremden Handoff ausführen und
keinen Systemschreibvorgang auslösen. Die einzige dauerhafte TDH-Mutation bleibt
`666TDH UPDATE` unter `runtime/REPO_UPDATE_AUTHORITY.md`.

## Evidenzbasierte Nutzerführung

Den geprüften Current, Zielidentität, vorhandenen Checkpoint, offenen Schritt,
HOLD, Gegenprobe und nächste sichere Aktion zur Anzeige bringen. Unbekannte
Aktivität niemals als Fortschritt darstellen. Routen nur anhand der aktuellen
Registry und der vom Nutzer direkt angegebenen Branchauswahl anbieten.
Quelle: `runtime/ui/view_model.py`, `runtime/ui/render_html.py`.

Keine Veränderung der Child-Versionswerte. FSE Source Vault extern und inert.
ChatGPT-Host-Abnahme bleibt `OPEN_NOT_VERIFIED` bis zur echten Interaktion.
