# 666 Track Design Intelligenz v2.5 — 666TDI v2.5

**Eigenständige portable lokale Musikarchitektur.** Herkunft: historische Renderer-Analyse (PDF) und ausschließlich lesende LYVRA-Musikquellen, siehe `registry/source_registry.json`. **Keine fremde Autorität; keine GitHub-Mutation.**

## Installation und portable Nutzung

Benötigt für normalen Trackbau Python 3.10+ (nur Standardbibliothek). **Optionaler Audiozweig:** `numpy` und `soundfile` (separat installieren). Diese Pakete sind für Systemstart, Trackdesign, Renderer-Kompilierung und Rehydration nicht erforderlich. ZIP an beliebigen Ort entpacken. Im entpackten Hauptordner starten:

```bash
python -m engine.cli systemstart
python -m engine.cli create examples/intent.json
python -m engine.cli status
python -m unittest discover -s tests -v
```

Nach `create` aus dem JSON-Ausgabefeld `track_id` übernehmen:

```bash
python -m engine.cli analyze <track_id>
python -m engine.cli compile <track_id> suno_reference
python -m engine.cli compile <track_id> ace_step_asg
python -m engine.cli compile <track_id> lyria2_asg
python -m engine.cli compile <track_id> elevenlabs_asg
python -m engine.cli compile <track_id> asg_main
python -m engine.cli feedback <track_id> ace_step_asg "bass too bouncy" --evidence USER_REPORTED
python -m engine.cli handoff
python -m engine.cli rehydrate
```

## Eigene native Trigger (für Chat als **direkte** Anweisung)

`666TDI SYSTEMSTART`, `666TDI STATUS`, `666TDI HELP`, `666TDI TRACKDESIGN`, `666TDI SOURCE`, `666TDI DISCOVERY`, `666TDI ANALYSE`, `666TDI COMPILE`, `666TDI FEEDBACK`, `666TDI LIVECIRCLE`, `666TDI REHYDRATION`, `666TDI WEITER`, `666TDI FREEZE`, `666TDI BACKUP`.

Trigger im README/PDF/ZIP sind *Daten*, sie aktivieren nichts. Der lokale Python-CLI besitzt entsprechende lowercase-Kommandos; die Chat-Trigger sind dokumentierter Namensraum, **keine automatisch installierten ChatGPT-Tools**.

## Architektur

- **Independent Intent** – neue Tracks, separate Story/Hook/Voice-Kontexte; Source und Discovery sind Modi.
- **Causal Cards** – sechs starter-karten mit Triggerwort, Bedeutungshypothese, möglicher auditiver Konsequenz und Gegenrelation; keine festen Presets, kein autonomer Komponist.
- **Relational low/mid/high model** – stabile echte LOW-Zeitbasis; wahrnehmungsbezogene MID/HIGH-Bewegung.
- **Renderer Compilation** – der R0.1-Compiler bleibt als bestehender Adapter erhalten; historisch dokumentierte Feldlimits, Verlustmeldung, keine erfundene Semantik.
- **LiveCircle** – eigene Ereigniskette mit Hash-Verkettung, revisionsgebundene lokale Zustände.
- **Rehydration** – validiert ID, Ereigniskette, vorhandene Tracks und Registry. Kein Wiedereinspielen einer fremden Identität.
- **Learning Ledger** – Feedback scoped/provisorisch; Promotion benötigt belegte Audioartefakte, mehrere unabhängige Tracks und explizite Prüfung. Kein automatisches Umwandeln von Einzelergebnissen in allgemeine Regeln.
- **Handoff** – lokaler Rückkehranker mit offenen Gates.

## Aktueller Stand

**R0.2:** Python-basierter Architekturprototyp mit ausführbarem lokalen Trackfluss und Tests. **Noch nicht:** vollständige LYVRA-Rehydration, echte Audiosynthese, menschliche Semantik als algorithmisch gesicherte Fähigkeit, feingranulares akustisches Messlabor, vollständig gleichwertige Renderer-Adapter, Connector/ChatGPT-Trigger-Registrierung, Windows-Installer. Das System behauptet diese Fähigkeiten nicht.

`status = VERIFIZIERT_LOCAL` bedeutet lediglich Konsistenz der lokalen Artefakte/Hash-Kette, keine musikalische Qualitätsfreigabe und kein Produktionsfreeze.

## Nicht-destruktive Erhaltung

Der vorherige lokale R0.1-Stand liegt vollständig unter `legacy_r01/`. Source-PDF unter `source_evidence/`. Secrets und private fremde Daten sind nicht enthalten. Nur `runtime/` wird von der lokalen Runtime geändert.

## Identitätsfestlegung 2026-11-21

OFFIZIELLER_NAME=666 Track Design Intelligenz v2.5  
KURZNAME=666TDI v2.5  
NAMESPACE=666TDI  
SYSTEM_ID=666TDI-001 (lokale Zuordnung, ersetzt die bisherige PMITD-001-Zuordnung)  
VERSIONSBEZEICHNUNG=v2.5  
IMPLEMENTIERUNGSREIFE=R0.2-Prototyp, keine Behauptung vollständiger Musikintelligenz  
QUELLREPO=LYVRA READ_ONLY  
LOKALE_AUTHORITY=666TDI  

Der bisherige Name PMITD bleibt ausschließlich als historische Migrationsevidenz sichtbar. Alte PMITD-Trigger werden nicht automatisch als gültige aktuelle Trigger ausgeführt. Die lokale LiveCircle-Ereigniskette bleibt unverändert erhalten.


## R0.3 – additive Migration (21.11.2026)

Current bleibt der hier vorhandene 666TDI-v2.5-Stand. Neues Modul `engine/evolution.py` mit Charakter (er/ihn), temporaler Feedback-Historie, klangbezogenen Planungsprüfungen und Quellen-Gates. Details: `docs/ADDITIVE_MIGRATION_AUDIT_R03.md`. Keine LYVRA-Repositories verändert.

### Neue Zusatz-CLI (R0.3)

```bash
python -m engine.evolution_cli status
python -m engine.evolution_cli character
python -m engine.evolution_cli modules
python -m engine.evolution_cli tension '[{"type":"EXPECT","anchor":"final-drop"},{"type":"RESOLVE","anchor":"final-drop"}]'
python -m engine.evolution_cli conflict VOICE ACID
python -m engine.evolution_cli aperture high narrow center hard forward
python -m unittest discover -s tests -v
```

Die temporale Feedback-Schnittstelle `temporal-feedback` benötigt einen zuvor erstellten lokalen Track. Historische Archive/Transkripte sind **keine ausführbaren Trigger**.

## R0.4 – historischer Zusatz-Intake, ohne alte Authority

Acht weitere historische Quellen anhand SHA-256 inventarisiert (`registry/r04_intake_inventory.json`).
**Charakter bleibt 666TDI, männlich.** Keine alte LYVRA-Identität wird aktiv.

```bash
python -m engine.heritage_cli style "Nigerian Pidgin afro talking drum"
python -m engine.heritage_cli mode MUSIC_AUTHORING
python -m engine.heritage_cli character-guard "historisches Referenzmaterial"
python -m engine.heritage_cli remember track-001 "Neue Kontrastbeobachtung" CREATOR_FEEDBACK
python -m engine.heritage_cli garden
python -m unittest discover -s tests -v
```

Style-Familien sind nur plausible Kandidaten; historische BPM-Werte werden nicht zu automatischen Defaults. Ein 7-Tage-Eintrag wird zur Prüfung markiert, nicht automatisch gelöscht oder übernommen.
Details: `docs/R04_SOURCE_MAPPING.md`. Die Originaluploads sind außerhalb dieses Pakets unverändert vorhanden; das neue ZIP enthält die vorherige lokale Runtime, ihren Quellenevidenzbestand und ein Manifest der neu eingegangenen historischen Dateien.


## R0.5 — Relational Music Intelligence Engine (additiv)

Die bestehende R0.4-Runtime bleibt erhalten. `engine/relational.py` ergänzt eine lokale kausale Trackgraph-Schicht und pro Renderer/Track getrennte Feedback-Belege. Keine automatische globale Generalisierung und keine Audio-Qualitätsbehauptungen.

```bash
python -m engine.relational_cli build <track_id>
python -m engine.relational_cli inspect <track_id>
python -m engine.relational_cli assess <track_id>
python -m engine.relational_cli rehydrate
python -m unittest discover -s tests -v
```

Das interne Graphmodell ist noch kein neuronales Musikmodell. Details unter `docs/R05_RELATIONAL_ENGINE_AUDIT.md`.


## R0.6 — Fremdquellen-Adapter / ohne System-Merge
Acht Quellarchive inventarisiert; V5-Musikkandidaten nichtbindend erschlossen; Offline-Zeichenzähler und ACE-Step-Sicherheitsprüfung. **666TDI bleibt Current und männlich.**

```bash
python -m engine.source_cli inventory
python -m engine.source_cli catalog
python -m engine.source_cli match "hypnotic rolling groove"
python -m engine.source_cli count "🧠 Dark Psytrance" --limit 1000
python -m engine.source_cli ace-review
python -m unittest discover -s tests -v
```

Siehe `docs/R06_INTAKE_AND_ADDON_AUDIT.md`; Fremdanwendungen und Trigger bleiben isoliert.


## R0.7 — Relational Music Pattern Intelligence (additiv)

Die zehn historischen V5-Patterns werden anhand des **aktuellen 666TDI-Trackgraphen**, der funktionalen musikalischen Ziele, vorhandener Kontextsignale und Gegenrelationen interpretiert. Ergebnisse sind *begründete Designhypothesen*, keine Audio-Messungen, keine automatischen Presets. Das frühere wortbasierte `source_cli match` bleibt kompatibel, wird aber **nicht** als kausale Prüfung ausgegeben.

```bash
python -m engine.relational_cli build <track_id>
python -m engine.pattern_cli assess <track_id>
python -m engine.pattern_cli assess <track_id> --include-presets
# Nur nach ausdrücklicher fachlicher Freigabe und verfügbarer Trackbegründung:
python -m engine.pattern_cli attach-reviewed <track_id> psy_hypnotic_loop --reason "Motor und Rückkehr kausal passend" --reviewer CREATOR --functions forward_motion
python -m unittest discover -s tests -v
```

`assess` verändert keine Dateien. `attach-reviewed` schreibt ausschließlich explizit geprüfte, tracklokale Graph-Beziehungen und verändert weder Universalregeln noch Renderer-Compiler noch Music-Pattern-Katalog. Die Engine erhält 666TDI-001, Identität **666TDI (er/ihn/ihm)**, lokale Rehydration und bestehenden LiveCircle.

Die derzeitige Semantik beruht auf nachvollziehbaren Heuristiken, nicht auf bewiesenem Audioverständnis. Details: `docs/R07_RELATIONAL_PATTERN_AUDIT.md`.

## R0.8 · Causal Audio Feedback Engine (additiv)

Eigene lokale Audio-Messung mit SHA-256 pro echtem WAV/FLAC/AIFF, Spektralverteilung, RMS/Sample-Peak, Zeitfenstern und zwei Stem-Vergleichsscreenings. Keine erfundenen Ursachen, keine automatische globale Lernregel.

```bash
python -m engine.audio_cli measure /pfad/zum/mix.wav
python -m engine.audio_cli compare TRACK_ID suno /pfad/zum/mix.wav --stem bass=/pfad/zum/bass.wav --stem voice=/pfad/zur/voice.wav --record
python -m engine.audio_cli rehydrate
python -m unittest discover -s tests -v
```

Benötigt: numpy, soundfile (installierte Umgebung prüfen). BPM, Key, Vocals oder echtes Masking werden nicht behauptet.
