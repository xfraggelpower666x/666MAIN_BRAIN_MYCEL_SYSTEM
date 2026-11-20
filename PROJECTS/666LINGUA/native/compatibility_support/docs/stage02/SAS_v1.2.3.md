# System Architecture Specification — LYVRA DOLMETSCHER v1.2.3

## 1. Architekturprinzip

Eine einzige interne Bootstrap-Wurzel initialisiert eine sitzungsgebundene Zustandsmaschine. Eingaben werden nicht durch parallele Systeme verarbeitet, sondern durch eine feste Pipeline bestehender Rollen.

## 2. Komponenten

1. **Package Discovery Pointer** — erkennt ein reales Paketereignis, ist selbst kein Bootstrap.
2. **Canonical Bootstrap** — prüft Identität, Manifest, Freeze, CRC und Systemsprache.
3. **Input Guard** — schützt Rohtext, Struktur und sensible Elemente.
4. **Language Detector / Router** — trennt Quelle, Ziel und Menüsprache; nutzt direkte Profilrouten.
5. **Context / Relationship / Emotion Analysis** — ermittelt Bedeutung, Beziehung, Ton und Subtext.
6. **Target Specialist / Translator** — erzeugt die zielsprachliche Fassung.
7. **Emoji Reinforcement** — ergänzt ausschließlich kausal passende Verstärkung.
8. **Quality Auditor** — prüft Semantik, Negationen, Sprecher, Format und Drift.
9. **HOLD / Task Stack** — verwaltet offene Ziele, Sammelmodi und Unterbrechungen.
10. **Lifecycle** — Audit, Reparatur, Freeze, Backup und verifizierter Restore.

## 3. Datenfluss

```text
ATTACHMENT_OR_TEXT
→ BOOTSTRAP_GATE
→ INPUT_GUARD
→ LANGUAGE_RESOLUTION
→ HOLD_OR_ROUTE
→ CONTEXT_AND_RELATIONSHIP_ANALYSIS
→ TRANSLATION
→ EMOJI_REINFORCEMENT
→ QUALITY_AUDIT
→ OUTPUT
→ CHECKPOINT_DELTA
```

## 4. Zustandsführung

Persistenz wird nicht vorausgesetzt. Sitzungszustände dürfen nur über definierte Checkpoint-Schemata exportiert und nach Hash-, Versions- und Konfliktprüfung rehydriert werden.

## 5. Integrationsgrenze Stage 02

Die Stage-02-Erweiterung ergänzt ausschließlich Dokumentation, Traceability, Registry-Passport und Audit-Evidenz. `ENGINE_MUTATION=0`, `LYVRA_CORE_MUTATION=0`, `666PFS_MUTATION=0`, `DRIVE_WRITE=0`.
