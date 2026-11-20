# LYVRA DOLMETSCHER v2.2.0

## Aktiver Stand

`SYSTEM_ID=LYVRA-DOLMETSCHER-001`
`CYCLE=03`
`STAGE=02`
`STATUS=LOCAL_FROZEN · STRUCTURAL_AUDIT_PASS`

R2P7 wurde als funktionierende Runtime-Referenz analysiert und erhalten.
v2.2.0 erweitert denselben Processing Orchestrator um ein sharebares
Vier-Ausgaben-Bundle:

- 💜 Hauptübersetzung
- 🌎 lokal natürlicher
- 📐 präzise / technisch
- ❤️ Emotional+

Die Hauptübersetzung bleibt semantische Autorität. Alle Alternativen werden aus
derselben geprüften Bedeutung abgeleitet.

### Emoji

Die bestehende kausale Emoji-Verstärkung bleibt erhalten und wird für normale /
emotionale Chats moderat verstärkt. Technische und sachkritische Texte bleiben
minimal.

### Teilen

Wenn der Host Writing Blocks / native Share-Funktionen unterstützt, bekommt jede
Fassung eine eigene teilbare Textfläche. WhatsApp/Nativ-Share darf nur als direkt
verfügbar behauptet werden, wenn der Host diese Fähigkeit tatsächlich anbietet.

---

# LYVRA DOLMETSCHER v2.1.1 · R2P7

## ZIP einfügen = Dolmetscher starten

Ein echtes, verifiziertes LYVRA-DOLMETSCHER-ZIP ist kein allgemeiner Dateianhang, sondern eine eindeutige Startanforderung.

```text
VALID ZIP ATTACHMENT
→ VERIFY IDENTITY / MANIFEST / FREEZE / CRC
→ LOAD SINGLE BOOTSTRAP ROOT
→ DETECT ACTIVE GPT/CHAT LANGUAGE
→ AUTO-SELECT AND LOCK MENU LANGUAGE
→ START LYVRA DOLMETSCHER
```

Nach erfolgreicher Prüfung ist die Frage „Was soll ich mit der Datei tun?“ verboten. Der Host startet unmittelbar LYVRA DOLMETSCHER. Liegt Begleittext vor, wird dieser nach dem Routing automatisch verarbeitet; andernfalls erscheint das Dolmetscher-Hauptmenü.

## Automatische Systemsprache

Die Menüsprache wird in dieser Reihenfolge ermittelt:

1. vom Host bereitgestellte GPT-/UI-/Locale-Sprache
2. aktive Sprache der GPT-Antworten im aktuellen Chat
3. dominante aktuelle Gesprächssprache
4. ausdrücklich bestätigte Nutzerpräferenz
5. Sprachauswahl nur als Fallback

Unterstützt werden Deutsch, International English, American English, British English, Español und Português do Brasil. Unklare, widersprüchliche oder nicht unterstützte Signale werden nicht geraten.

## Fallback-Startbefehle

```text
LYVRA DOLMETSCHER START
LYVRA INTERPRETER START
START LYVRA INTERPRETER
```

## First use for external recipients

- `00_LYVRA_DOLMETSCHER_AUTOBOOTSTRAP.md`: host discovery/start pointer
- `01_START_HERE_USER.md`: simple instructions for a recipient with no prior system knowledge
- `PORTABLE_START.md`: portable host/recipient startup contract

## Dateien

- `00_LYVRA_DOLMETSCHER_AUTOBOOTSTRAP.md`: sofort sichtbare Paket-Startanweisung
- `LYVRA_DOLMETSCHER_SYSTEM_PROMPT_v2.1.1.md`: vollständiger Agentenprompt
- `bootstrap/LYVRA_DOLMETSCHER_BOOTSTRAP_v2.1.1.md`: einziger kanonischer Bootstrap
- `config/lyvra_dolmetscher_config_v2.1.1.json`: maschinenlesbarer Start- und Sprachvertrag
- `tests/cases.json`: kanonischer 100-Fälle-Basissatz; zusätzliche Stage-/Runtime-Testsets liegen ebenfalls unter `tests/`
- `PORTABLE_R2P7_EXTERNAL_VISIBILITY_REPAIR_AUDIT.json`: aktiver Portable-Reparatur-/Konsistenznachweis
- `PORTABLE_FREEZE.json`: aktiver Portable-Freeze
- `PORTABLE_SHA256SUMS.txt`: aktive Paket-Prüfsummen
- `recovery/`: Recovery-Unterlagen

## Legacy-Dateien in R2P7

Die parallel enthaltenen v2.1.0-Dateien bleiben als historische/Kompatibilitäts-Snapshots erhalten. Für den Start sind sie **inert**. Maßgeblich sind ausschließlich `PORTABLE_MANIFEST.json` und dessen exakte v2.1.1/R2P7-Pointer.

## Systemgrenze

```text
LYVRA_CORE_MUTATION=0
666PFS_MUTATION=0
DRIVE_WRITE=0
SECOND_BOOTSTRAP=0
SECOND_UPDATE_ROUTE=0
CENTRAL_LYVRA_INTEGRATION_HANDOFF=ABSENT
```

## Stage-02-Dokumentation

Die v2.0.0-Freigabe ergänzt die in v1.2.2 fehlende formale Entwicklungsdokumentation:

- `docs/stage02/SRS_v1.2.3.md`
- `docs/stage02/SAS_v1.2.3.md`
- `docs/stage02/ENGINE_SPECIFICATIONS_v1.2.3.md`
- `docs/stage02/REQUIREMENT_TRACEABILITY_v1.2.3.json`
- `docs/stage02/MASTER_AUDIT_v1.2.3.md`

Diese Schicht ist dokumentarisch. Die Laufzeitengine blieb unverändert.

## 666PFS-Intake-Referenz v2.0.0

Dieses Paket entwickelt **kein 666PFS-System**. Die enthaltene Referenz `docs/PFS_EXTERNAL_INTAKE_REFERENCE_POLICY_v1.7.0.md` ist inert und dokumentarisch; sie erteilt keine Registry-, Pointer-, Menü- oder Drive-Autorität. Autorisierte Registry-, Pointer-, Menü- und Drive-Schritte bleiben außerhalb dieses Pakets.


## v2.0.0 — Stage-03 Runtime Validation

- Korrektur-vs.-Neunachricht praktisch modelliert
- konservative Diktierrekonstruktion
- Intent-/Rollentrennung
- mehrdimensionale menschliche Kommunikation
- Typografie- und Output-Integrity
- Confidence-Evidenz
- optionaler 🧐🦆-Companion
- 48/48 lokale Runtime-Fälle PASS
- echte Sprachmodellruntime weiterhin offen


## v2.0.0 — Stage 04 Release Candidate

- 30/30 direkte Sprachprofilrouten geprüft
- 12/12 anspruchsvolle Sonderfälle geprüft
- 42/42 Stage-04-Fälle PASS
- Release-Candidate-Freeze
- vollständige Systemsicherung
- keine unabhängige Zertifizierung behauptet


## v2.0.0 — Stage 05 Evolution

- kontrolliertes Korrekturlernen ohne stille globale Writes
- Context Continuity Ledger mit Hash-first-Datensparsamkeit
- Human-Review-Feedback und Konfliktquarantäne
- Device-/Share-Adaptervertrag
- Privacy/Data-Minimization und Forget-Pfad
- Regressionstest-Kandidaten
- Evolution Proposal Queue
- nächster Zyklus startet wieder bei Stage 01


## v2.0.0 — Cycle 02 Stage 01

- „Stage 06“ vertragskonform als neuer Zyklus Stage 01 aufgelöst
- sieben Evolutionskandidaten analysiert
- fünf Stage-02-Komponenten konsolidiert
- 20 verbindliche Anforderungen
- Retention-/Deletion-Modell
- Human-Review-Autoritätsmodell
- Device-Acceptance-Plan
- 45/45 Analyseprüfungen PASS
- keine Runtime-Aktivierung und kein Freeze
