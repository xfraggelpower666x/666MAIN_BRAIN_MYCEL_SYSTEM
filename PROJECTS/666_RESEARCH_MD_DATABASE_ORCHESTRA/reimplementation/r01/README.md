# 666 RESEARCH MD DATABASE ORCHESTRA — getrennte Wiederimplementierung R01

**Identität:** `REIMPLEMENTATION_R01` · **Version:** `0.1.0` · **Status:** `VERIFIED_REIMPLEMENTATION_SUBSET` (nicht produktiv, keine historische Recovery-Freigabe).

Diese additive, ausschließlich lesende Laufzeit unter `reimplementation/r01/` implementiert nur die anhand der erhaltenen Originale nachweisbaren Kernfunktionen: SHA-256-Prüfung, getrennte Themen-/Prompt-Registry, ID- und Inhaltsrecherche einschließlich Einträgen und Quellen, Datenaudit, reine Promptvorlagen-Variablenersetzung sowie JSON/Markdown-Ausgabe an `stdout`. Keine Internetrecherche, Audiodateien, Speicherung von Nutzerergebnissen oder automatische Generierung.

## Start (Repository-Root)

```bash
node reimplementation/r01/cli.js status
node reimplementation/r01/cli.js menu
node reimplementation/r01/cli.js search psycho
node reimplementation/r01/cli.js get chaos-001
node reimplementation/r01/cli.js topic chaos-theory
node reimplementation/r01/cli.js sources chaos-theory
node reimplementation/r01/cli.js prompt chaos-psytrance-suno-prompt-specialist
node reimplementation/r01/cli.js render chaos-psytrance-suno-prompt-specialist --var=bpm=148
node reimplementation/r01/cli.js export json
node reimplementation/r01/cli.js export md
node reimplementation/r01/cli.js audit
cd reimplementation/r01 && npm test
```

Ausgabe wird nur auf der Konsole erzeugt. Wer einen Export dauerhaft speichern möchte, entscheidet dies durch eigene Shell-Umleitung und legt ihn **außerhalb dieses System-only-Repositories** ab. Kein automatischer Export nach `output/`.

## Schutzgrenzen

- Drei historische Original-JS-Dateien sowie das v1.7.1-Dateimanifest werden **nur gelesen**, niemals geändert.
- Vor dem Auswerten wird jede Quelldatei gegen das historische SHA-256-Manifest geprüft. Nicht passende oder fehlende Inhalte blockieren.
- Originalmodule werden ausschließlich in einer begrenzten Node-VM ohne `require`, `process`, Netzwerk, Worker oder Codegenerierung geladen.
- Validierung kontrolliert IDs, Quellenverknüpfungen und historische Statusklassen. Falsche Eingaben werden abgewiesen.
- Die Promptfunktion interpoliert nur deklarierte Variablen der erhaltenen Originalvorlage; sie erstellt keine neuen Musikstücke und behauptet keine erfolgreichen Suno-Generationen.
- Die drei historischen Originale bleiben erhalten; weder Registry noch Original-Bootstrap v1.7.1 werden als vollständig rehydriert erklärt.

## Offen

123 von 136 historischen Quell-/Dokumentdateien sind im Recovery-Worktree nicht verfügbar. Der produktive historische Freeze bleibt unangetastet. Fehlende Originalmodule (Bootstrap, Stem-, Sonification-, Blind-A/B- und FX-Pipelines usw.) müssen gesondert rekonstruiert oder durch getrennte neue Implementierungen ersetzt werden, nie unter vorgetäuschter Originalidentität.
