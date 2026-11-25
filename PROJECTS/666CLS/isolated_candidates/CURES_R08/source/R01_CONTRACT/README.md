# 666CURES — Isolierter Funktionsvertrag R01

**Status:** `PROPOSED_ISOLATED_NONEXECUTABLE` · `PFS CURES HOLD` · `NO_REPOSITORY_WRITES`

**Quelle:** das vom Nutzer hochgeladene `666CURES__CURES-16001-20261122T111459Z-1-001.zip` (`SHA-256: 140fd87c1bbcb80d90fcbcd4aa4da52761eb043ea36a7090c50346f339da3241`).
Innerer historischer Canonical-Stand: `666CURES_SYSTEM_v0.1.0.md`; Purpose-Korrektur `v0.1.1`.
Die acht inneren Manifestbindungen wurden gegen die tatsächlichen Bytes überprüft (`8/8 PASS`).

## Einordnung

Dieses Paket enthält **keine CURES-Engine**. Es enthält einen überprüfbaren fachlichen Sollvertrag und einen optionalen Testtreiber für eine später getrennt autorisierte Kandidatenimplementierung.
Der aktuelle PFS-Zustand bleibt `HOLD_FUNCTIONAL_PAYLOAD_SOURCE_NOT_FOUND`. Dieses Paket darf weder als wiedergefundenes Original noch als veröffentlichte PFS-Runtime bezeichnet werden.

## Dateien

- `contracts/CURES_CONTRACT_R01.json` – Pflichtstruktur, Isolation, Invarianten, geplante Kandidatenschnittstelle.
- `fixtures/cases.json` – zehn illustrative Ein-/Ausgabefälle inklusive Negativbedingungen.
- `tests/test_contract.py` – überprüft die Konsistenz dieses **Vertrags**, nicht die Funktionsfähigkeit einer Engine.
- `tools/check_candidate.py` – optionaler Smoke-Test einer **extern bereitgestellten und vertrauenswürdigen** Python-Implementierung.
- `evidence/SOURCE_BINDINGS.json` – genaue Herkunft, Archivprüfsummen und bestehende PFS-HOLD-Grenze.

## Ausführen (lokal, keine Fremdaktivierung)

```bash
python -m unittest discover -s tests -v
```

Nur nach eigener separater Kandidatenfreigabe:

```bash
python tools/check_candidate.py /absoluter/pfad/zum/vertrauenswuerdigen/candidate.py
```

Das zweite Kommando **importiert und führt** Kandidatencode aus: niemals mit unbekannten oder unkontrollierten Dateien durchführen. Markerprüfungen sind nur Smoke-Tests. Für eine echte Funktionsabnahme sind zusätzlich menschliche Semantikprüfung, vollständige Reverse-Mapping-Prüfung, Negations-/Unsicherheitsfälle, ausführbare Isolation und native Owner-Readbacks erforderlich.

## Herkunft vs. vorgeschlagene Ergänzung

*Originalquellen:* v0.1.0 Identität, Parent/Child, Causal Learning Bridge, Provenienz, kein Shared State, kein globaler Controller. v0.1.1 Fulltext-Purpose, Bedeutung/Relation/Kausalität/Kontext, unbekannt bleibt unbekannt, keine erfundenen Regeln/Authority.

*R01-vorgeschlagen:* JSON-Schema der Testeingaben, Python-Signatur, konkrete Beispieltexte, Testdateien, technische Markerprüfung. Diese Bestandteile sind **keine** historischen Originalteile.

## Unverändert

CLS v1.24.11; PFS/CURES Root und HOLD; CLIC; LYVRA; CLINT; keine Repository-, Drive- oder Provider-Writes.
