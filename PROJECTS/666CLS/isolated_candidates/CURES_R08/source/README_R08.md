# 666CURES – isolierter Kandidat R08

**Identität:** neuer deterministischer CURES-Engineering-Kandidat; **nicht** wiedergefundene Originalengine. Keine PFS-, CLS-, CLIC- oder LYVRA-Runtime-Reaktivierung.

## Änderungen gegenüber R07
- `candidate/trust_rotation_r08.py`: `verify_rotated_sources(documents, envelope, external_trust_policy, *, minimum_sequence, rotation=None, revocation_events=None, minimum_event_sequence=0)`.
- Ed25519-Rotation mit alter und neuer Unterschrift; zusätzlich muss die vollständige Rotation in einem **extern authentifizierten** Vertrauensregelwerk per SHA-256-Fingerprint freigegeben sein.
- Empfänger muss unveränderliche, unabhängig bezogene öffentliche Schlüssel und **monoton persistierte** Sequenz-Minima übergeben. Der Kandidat speichert sie absichtlich nicht selbst.
- Signierte Widerrufsereignisse für Dokumente und Schlüssel; Prüfung von Signaturen, Aussteller, Ereignis-ID, Reihenfolge und externer Mindestsequenz.
- Historische R01–R07-Dateien werden bytegenau erhalten; neues R08-Modul ist additiv.
- `integrations/CLS_REFERENCE_INTERFACE_R08.json`: **nur Vorschlag einer nicht ausführenden Anzeige**. Nicht in CLS publiziert.
- `PFS_OWNER_INTEGRATION_DECISION_R08.md`: offenes Owner-Gate; **keine PFS-Mutation**.

## Grenzen
Eine mit einem Schlüssel signierte Datei beweist ausschließlich die Kontrolle über den zugehörigen privaten Schlüssel. Der Codetest authentifiziert weder reale Ausstelleridentität noch historische Provenienz oder Kausalwahrheit. Eine externe, unabhängige Owner-Attestierung liegt nicht vor. Testschlüssel sind kurzlebig und werden nicht als produktive Identität ausgegeben.

Hinweis zum Replay-Schutz: Er hängt von einem **extern authentifizierten, dauerhaften, monotonen Speicher** für Mindestsequenzen ab. R08 bewahrt diesen Zustand absichtlich nicht autonom und behauptet deshalb keine durchgängige Betriebsabsicherung.

## Lokale Befehle
```bash
python -m unittest discover -s tests -p 'test_candidate_*.py' -q
python -m unittest discover -s R01_CONTRACT/tests -p 'test_*.py' -q
python R01_CONTRACT/tools/check_candidate.py candidate/cures_candidate.py
```

Abhängigkeit: `cryptography>=46,<47` aus erhaltener `requirements-r07.txt`. Kein Netzwerk, kein Streaming, keine bezahlten Dienste, kein Auto-Load.

## Native Quellenstatus
PFS `xfraggelpower666x/666PFS_CSM/main` HEAD `08989d5dc71259cbebf108c71d2e315aa9ac28a1`: `CURES-16001` weiterhin `HOLD_FUNCTIONAL_PAYLOAD_SOURCE_NOT_FOUND`, `CHILD_AUTOLOAD=FORBIDDEN` (GitHub Readback). Der parallele CLS Shared-Branch hat sich bis `a1784d2c706f75c97c676fecf37f379a6ac7b4f7` verändert; der früher bekannte CLS-Verzeichnispfad lieferte beim heutigen Aufruf 404. CLS-Current wurde daher **nicht** erneut verifiziert, eine CLS-Integration ist `READBACK_PENDING`.

## Governance
Angegebenes Engineering-Ziel: LYVRA Coding Profi koordiniert CodeForge-Fähigkeiten. Belegt genutzt wurden der 666DEV-Python-Engineering- und Quality-Gates-Skill als Entwicklungsanweisung; eine tatsächliche delegierte parallele Plugin-Ausführung wird nicht behauptet. Alle anderen Systeme behalten ihre native Authority.
