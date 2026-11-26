# 666TDI v2.5 — R0.6 Source Intake & Additive Integration Audit

## Current & Identity
- CURRENT: 666TDI v2.5 R0.5 (lokaler Ausgangsstand)
- System: `666TDI-001`, Charakter: **666TDI (er/ihn/ihm)**
- LYVRA: Historical provenance only; never copied as live identity
- Runtime: no GitHub writes, no third-party code execution, no network, no foreign trigger activation

## Acht Quellen — Zuordnung und Abgrenzung
1. **JSON Karten DEU/ENG**: 24 Themen / 48 Sprachkarten, nicht musikalische Card-Graph-Livekarten. Enthält Veröffentlichungs-, Kontakt- und Rechtsthemen; INVENTORY_ONLY, keine Übernahme personenbezogener Felder.
2. **Intelligent UI Template 0.85.1**: UI-Konzept und Visual-Daemon-Vorlage. Kein fremder Bootstrap und kein aktiver Visual-Agent. TEMPLATE_REVIEW_ONLY.
3. **System Build Control Kernel v6.7**: Audit/Freeze/Manifest/Pointer-Methodik. Fremde Pointer sind inert. GOVERNANCE_REFERENCE_ONLY.
4. **ACE-Step Integrated Code**: ComfyUI/DAW/Services mit eigener Abhängigkeit, Lizenz und lokal/Cloud-Transport. Eigene Backend-Installation erforderlich; Integration als capability/transport review, **keine Cloud-Ausführung oder API-Key-Übernahme**.
5. **Universal CodeForge 1.4.0**: eigenständige Code-/Deployment-Governance, **kein Musikfacetten- oder Trigger-Merge**. REFERENCE_ONLY.
6. **Visual Character Auditor 1.2.0**: Unicode-/UTF-16-/UTF-8-Zählmethoden, lokal als eigenständige Zählfunktion umgesetzt. Externer Auditor nicht verändert; keine behauptete volle Featureparität.
7. **V5 Hybrid Final**: Pattern-/Preset-Katalog als historische **kreative Kandidaten** eingelesen. Keine festen BPM-Werte, kein Reaktivieren alter Songvorlagen, kein automatisches Card-Promotion.
8. **V5 Integration Audit Repair Freeze Backup**: Web-Control-Panel und Reparaturnachweise. Nicht in Python-Runtime gemergt, UI-Kompatibilität offen.

## Reale Umsetzung
- `registry/r06_intake_inventory.json`: Originalarchiv-Hashes, CRC, Dateizahl, Kandidatenstatus.
- `registry/r06_music_candidates.json`: ausgewählte nichtbindende Track-Pattern-/Preset-Metadaten.
- `engine/source_adapters.py`: verifizierende Registry, katalogbezogene Pattern-Vorschläge, Zeichenmessung, ACE-Step-Sicherheitsgrenze.
- `engine/source_cli.py`: eigener manueller CLI-Readback.
- `tests/test_source_adapters.py`: Regressionen (Trennung, Identität, Unicode, keine Auto-Aktivierung).

## Grenzen und offene Gates
- Keine vollständige Audio-Renderer-Integration, keine Stem- oder Audio-Auswertung, keine LLM-Musikintelligenz aus Fremdcode.
- ZIP-Inventar == Bestand, nicht gleich funktionale Rehydration. Asset-/Lizenzprüfung vor jeder Übernahme fremden Quellcodes.
- V5-Creative-Patterns sind nur Hypothesen; empirische Verifikation und Gegenbelege bleiben erforderlich.
- Der neue Zeichenzähler zählt Codepoints, UTF-16-Units oder Bytes; grapheme clusters nicht implementiert.
- Repository-Current ist unabhängig, Source-Archive keine native 666TDI-Autorität.
