# 666 RESEARCH MD DATABASE ORCHESTRA

**Version:** v1.7.0  
**Status:** LOCAL RELEASE / AUDITABLE / MODULAR

Modulare, lokale JavaScript-Recherche- und Prompt-Datenbank mit Chaos-/Psytrance-/Psychoakustik-Spezialist:

- Manifest-gesteuertem Bootstrap
- getrennten Themen-Dateien
- kanonischer Prompt-Registry
- Offline-Promptbibliothek
- lokalem Prompt-Manager
- deterministischem Agenten-Orchestrator
- Volltextsuche
- lokalen Rechercheentwürfen
- Markdown- und JSON-Export
- messbarem Daten-, Prompt-, Routing- und Dateisystem-Audit
- Funktionstests und SHA-256-Prüfsummen

## Inhaltsverzeichnis

1. Start
2. Architektur
3. Recherchethemen
4. Promptbibliothek
5. Orchestrator
6. Audit und Export
7. Neues Thema
8. Neuer kanonischer Prompt
9. Speichergrenzen
10. Wiederherstellung

## Start

### Browser

```bash
cd 666_RESEARCH_MD_DATABASE_ORCHESTRA_v1_2_0
python3 -m http.server 8080
```

Dann `http://localhost:8080/app/` öffnen.

### Tests, Audit und Export

```bash
npm run build
```

Erzeugt im Ordner `output/`:

- `SYSTEM_AUDIT.json`
- `SYSTEM_AUDIT.md`
- `research-index.json`
- `prompt-index.json`
- `PROMPT_LIBRARY_EXPORT.md`
- `PROMPT_LIBRARY_EXPORT.json`
- `RESEARCH_DATABASE_EXPORT.md`
- `SHA256SUMS.txt`

## Architektur

```text
Manifest
→ Bootstrap
→ Core Modules
→ Feature Modules
→ Topic Databases
→ Prompt Modules
→ Menu / Search / Audit / Export
```

Recherchewissen und Promptbibliothek nutzen getrennte Registries. Der lokale Prompt-Manager führt beide nur für Suche und Export zusammen.

## Recherchethemen

Jedes Thema liegt als separate Datei unter `data/topics/topic-*.js`.

## Promptbibliothek

- Kanonische Promptmodule: `data/prompts/*.js`
- Lesbare lokale Bibliothek: `prompts-library/categories/**/*.md`
- Statischer Index: `prompts-library/index.json`
- Browserlokale Entwürfe: `localStorage`

## Orchestrator

Unterstützte Artefakte:

- BRD
- TestCase
- UserStory
- DataverseTable
- PowerApp
- Flow
- FAQ
- SOP
- Title
- Paragraph

Mehrdeutige Primärausgaben erzeugen genau eine Klärungsfrage.

## Neues Thema

1. `templates/TOPIC_MODULE_TEMPLATE.js` kopieren.
2. Eindeutige IDs setzen.
3. Als `data/topics/topic-*.js` speichern.
4. Im Manifest registrieren.
5. `npm run build` ausführen.
6. Audit prüfen.

## Neuer kanonischer Prompt

1. `templates/PROMPT_MODULE_TEMPLATE.js` kopieren.
2. Eindeutige Prompt-ID und Version setzen.
3. Variablen deklarieren.
4. Unter `data/prompts/` speichern.
5. Manifest ergänzen.
6. `npm run build` ausführen.

## Speichergrenzen

Browserentwürfe und lokale Prompts in `localStorage` überschreiben keine kanonischen Quelldateien. Eine automatische Browser-Rückschreibung in JavaScript-Dateien ist absichtlich nicht enthalten.

## Wiederherstellung

1. `MASTER_PROMPT.md`
2. `HANDOFF.md`
3. `system/config/system-manifest.js`
4. `system/bootstrap-loader.js`
5. `system/core/*.js`
6. `system/modules/*.js`
7. `data/topics/*.js`
8. `data/prompts/*.js`
9. `prompts-library/index.json`
10. `npm run build`


## Neuer v1.3.0-Zweig

- `docs/topics/CHAOS_PSYTRANCE_PSYCHOAKUSTIK_4D_5D_SUNO_PROMPT_SPECIALIST.md`
- `data/topics/topic-chaos-psytrance-psychoacoustics.js`
- `system/modules/chaos-psytrance-prompt-specialist.js`
- `data/prompts/prompt-chaos-psytrance-suno-specialist.js`

Jede abgeschlossene Themen-MD endet mit 3–5 priorisierten Anschlussrecherchen.


## v1.4.0 · Adaptive Musikmanifestation

Neu integriert:

- Predictive Tension
- Embodied Pressure
- Spectromorphology
- Sonification
- Adaptive Manifestation
- ausführbarer Suno-v5.5-Prompt-Spezialist
- fünf priorisierte Anschlussrecherchen nach jedem Forschungsabschluss

Zentrale Forschungs-MD:

`docs/topics/PREDICTIVE_TENSION_EMBODIED_PRESSURE_SPECTROMORPHOLOGY_SONIFICATION_ADAPTIVE_MANIFESTATION.md`


## v1.5.0 · Complete Post-v1.4.0 Capture

Neu gespeichert:

- `docs/system/POST_V1_4_0_CAPTURE_REGISTER.md`
- `docs/topics/SUNO_5_5_PRO_HINTS_FIVE_SYSTEMS.md`
- `docs/topics/PROMPT_EXAMPLES_SPECIALITIES_FIVE_SYSTEMS.md`
- `docs/topics/PSYCHOACOUSTIC_HYBRID_MODE_PROMPT_SYSTEM.md`
- `data/topics/topic-suno-55-psychoacoustic-hybrid-prompting.js`
- `data/prompts/prompt-psychoacoustic-hybrid-six-system-specialist.js`
- `data/prompts/prompt-suno-55-five-system-ab-test-register.js`
- `system/modules/psychoacoustic-hybrid-prompt-specialist.js`

Der neue Release behebt die Prozesslücke, bei der fertige Chat-Ausgaben nicht automatisch in Datenbank, Promptbibliothek, Audit und Systemsicherung übernommen wurden.


## v1.5.1 · Five-System Core Priority Freeze

Die fünf Systeme Predictive Tension, Embodied Pressure, Spectromorphology, Sonification und Adaptive Manifestation sind jetzt als `CRITICAL PROTECTED CORE` maschinenprüfbar eingefroren.

Geschützt werden:

- Solo-Prompts,
- Prompt-Sonderheiten,
- Suno-v5.5-Hinweise,
- A/B-Testregister,
- psychoakustische Hybrid-Prompts,
- ausführbare Spezialisten,
- vollständige Forschungs- und Datenbankmodule.

Kanonische Governance-Datei:

`docs/governance/FIVE_SYSTEM_CORE_PRIORITY_FREEZE.md`


## v1.6.0 · Five-Branch Expansion

Neue Solo-Systeme:

- Psychoacoustic Frequency Masking Matrix
- Hybrid Preset Library
- Suno v5.5 A/B Lab
- Spectromorphological FX Dictionary
- Sonification Mapping Registry

Jeder Zweig besitzt eine eigene Forschungs-MD, ein Datenbankthema, ein Promptmodul, ein ausführbares Modul und vollständige Vier-Codebox-Beispiele. `FiveBranchMusicOrchestrator` verbindet die Zweige zusätzlich, ohne Solo-Ausgaben zu ersetzen.


## v1.7.0 · Audio Analysis and Upload Pipelines

### Real stem analysis

```bash
python3 tools/stem_masking_analyzer.py --input input/stems --output output/stem-analysis
```

### Sonification render

```bash
python3 tools/sonification_audio_pipeline.py   --input input/sonification/user-data.csv   --output output/sonification-upload   --columns x,y,z
```

### Complete build

```bash
npm run build
```

The build runs Node tests, both Python audio self-tests, database export, audit and checksums.
