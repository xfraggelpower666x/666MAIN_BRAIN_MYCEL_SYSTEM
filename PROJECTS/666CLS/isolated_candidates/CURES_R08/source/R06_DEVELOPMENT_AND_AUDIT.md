# 666CURES R06 · Entwicklungs- und Auditnachweis

## Umfang
- **Erhalten:** sämtliche R01–R05-Verträge, ursprüngliche `reconstruct`- und `reconstruct_sources`-Einstiegspunkte, historischen Testnachweise und Dateien.
- **Additiv:** `candidate/source_registry_r06.py` mit `verify_sources(documents, registry)`, zusätzliche Negativtests, Quellenregister-Fixtures, rein deklarative CLS-Referenz R06.
- **Keine** automatische Registrierung, Aktivierung, Änderungen an PFS/CLS/CLIC, Drive oder Live-Systempointer.

## Funktionsbeweis (lokal)
- R01-Vertragstests: **6/6**.
- R02–R06-Kandidatentests: **81/81**.
- R01-Smoke-Fälle: **10/10**.
- Summe: **97** getestete Fälle/Checks; Tests haben ausschließlich eine isolierte deterministische Kandidatenfunktion evaluiert.
- R06-Negativfälle: geänderte Inhalte und Zeiten, fehlende bzw. doppelte Registrierungen, gefälschte Quellen-Gruppen, unerwartete Ausführungsflags, Pseudocode-Injection, unklare natürliche Sprache, Konflikt- und Zeitprioritätsfälle.

## Verlässlichkeit und Grenzen
- SHA-256 gegen vom Aufrufer separat bereitgestelltes Register belegt **nur Integrität relativ zu genau diesem Register**.
- Autor, Datenherkunft, Historie, Independent Verification, Registry-Signatur, Vertrauen in den Register-Transport und die Wahrheit von Kausalbehauptungen bleiben **nicht verifiziert**.
- Es gibt keine automatisch vertrauenswürdige `source_group`, keine Stimmgewichtung, keine Zeitüberschreibung, keine automatischen Lern-Promotions.
- Register und Dokumente müssen aus getrennt geprüften Quellen kommen; die R06-Engine selbst ist keine Zertifizierungsstelle.

## Native Grenzen
- PFS `main` HEAD `08989d5dc71259cbebf108c71d2e315aa9ac28a1` frisch gelesen.
- `CURES-16001` bleibt `HOLD_FUNCTIONAL_PAYLOAD_SOURCE_NOT_FOUND`, `CHILD_AUTOLOAD=FORBIDDEN`.
- `CLS_REFERENCE_INTERFACE_R06.json` ist ausschließlich **PROPOSAL_ONLY_NOT_APPLIED**.
- **ORIGINAL_ENGINE_NOT_FOUND; LOCAL_R06_CANDIDATE_NOT_NATIVE_AUTHORITY; NO_REPOSITORY_WRITES.**

## Nächste sinnvolle Entwicklungspunkte
1. Unabhängiges Signatur-/Key-Trust-Gate mit echten, vom Besitzer genehmigten Vertrauensankern definieren.
2. Konfliktfälle aus mehreren Zeitachsen und Quellrevisionen mit gesicherter Chain of Custody prüfen.
3. Nicht ausführende CLS-Referenz gegen neu gelesenen CLS-Current integrieren, nur unter separatem `666CLS UPDATE`.
4. PFS-Owner-Audit und Integrationsfreigabe für einen Kandidaten strikt getrennt von der historischen Original-Engine entscheiden.
