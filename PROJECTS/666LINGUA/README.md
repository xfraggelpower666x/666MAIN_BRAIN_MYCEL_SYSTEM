# ◈🌐 666LINGUA fürs ChatGPT-Fenster

Eigenständiges Chat-Framework von 666SOUNDsDESIGn. Native Identität: `LYVRA-DOLMETSCHER-001`. Die öffentliche Repo-Ausgabe basiert auf dem verifizierten Drive-Stand **v3.4.6/R18** und ergänzt die Chat-Entsprechungen der Windows-App **1.4.0**.

## Start in einem neuen Chat

1. Kopiere den Block aus [START_HERE.md](START_HERE.md) in einen ChatGPT-Chat mit GitHub-Zugriff. Der Einstieg liest [CURRENT_POINTER.json](CURRENT_POINTER.json) und lädt die referenzierten Dateien aus **demselben Commit**.
2. Wenn du schon einen privaten Übergabestand hast, füge ihn als Anlage hinzu. Beim Erststart bietet 666LINGUA Englisch für die Oberfläche und Englisch → Deutsch als Standard an. App-Sprache, Sprachrichtung und Zeitzonen sind getrennt.
3. Verwende nach dem Laden die Menübefehle oder füge direkt den zu übersetzenden Text ein. Mit `666LINGUA HANDOFF` erhältst du den Stand für einen neuen Chat als JSON zum Kopieren.

Für die Übersetzung ist ChatGPT selbst die Sprachlaufzeit. Ein installiertes Programm, Python, Go oder ein externer Übersetzungsdienst sind dafür nicht erforderlich. Der Start über GitHub braucht einen bestätigten Lesezugriff. Falls der Chat GitHub nicht lesen kann, lade `CURRENT_POINTER.json` sowie dessen aufgeführte Pflichtdateien aus **einem** Commit herunter und hänge sie zusammen an. Ein so gestarteter Chat kann aus der Anlage arbeiten und meldet den aktuellen Branch-Readback als offen.

## Nativer LiveCircle

Der Pointer lädt den originalen R18-Bootstrap, die native Triggerliste, den LiveCircle, die Facetten und die Rehydrations- und Fortsetzungsverträge direkt. Der Chat-Adapter bindet deren Current- und Zustandszugriffe an GitHub und den privaten Handoff. Die zusätzlichen Chat-Befehle rufen die jeweilige native Funktion auf oder bedienen eine Windows-Funktionsentsprechung.

Google Drive ist ausschließlich Historie. Bei Live-Änderungen prüft der [LiveCircle](runtime/LIVECIRCLE.md), ob die Windows-App angepasst werden muss.

## Bedienung

| Funktion | Befehl |
| --- | --- |
| Start, Status, Hilfe und Fortsetzung | `666LINGUA SYSTEMSTART`, `666LINGUA STATUS`, `666LINGUA HELP`, `666LINGUA WEITER` |
| Oberfläche, Sprachpaar, Profil | `666LINGUA LANGUAGES`, `666LINGUA PROFILE`, alternativ `666LINGUA SPRACHEN` und `666LINGUA PROFIL` |
| Begriffe pro Richtung | `666LINGUA DICTIONARY` oder `666LINGUA WÖRTERBUCH` |
| Korrekturen, Kontext, Varianten | `666LINGUA LEARNING`, `666LINGUA EVIDENCE`, `666LINGUA VARIANTS` |
| Kopierblöcke und Emoji-Auswahl | `666LINGUA COPY SOURCE`, `666LINGUA COPY TARGET`, `666LINGUA EMOJI` |
| Zeitkontext und Umrechnung | `666LINGUA TIME` oder `666LINGUA UHRZEIT` |
| Privater Export und Wiederaufnahme | `666LINGUA HANDOFF`, `666LINGUA NEW CHAT`, `666LINGUA RESTORE` mit bestätigter Anlage |
| Native Wartung und Force Lock | `666LINGUA UPDATE`, `666LINGUA FORCE STATUS`, `666LINGUA FORCE ON`, `666LINGUA FORCE OFF` |

Jede Fassung hat einen eigenen Kopierblock. Die Ansichten für Profil, Wörterbücher, Zeit, Lernen und Belege erscheinen als separate Antworten im selben Chat. Die ChatGPT-Oberfläche stellt Kopierbuttons, Auswahl- oder Dialogelemente bereit, soweit der Host sie anbietet. Die Chat-Sitzung merkt sich bestätigte Eingaben im verfügbaren Kontext. Chatübergreifende Wiederaufnahme erfolgt über den privaten Export. Das GPT-Framework schreibt persönliche Daten nicht in das öffentliche Repository.

[Migration und Windows-Funktionsabgleich](provenance/MIGRATION.md) · [Abnahmeszenarien](tests/HOST_ACCEPTANCE.md)
