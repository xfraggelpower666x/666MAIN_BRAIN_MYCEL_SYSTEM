# 666CLS Main LiveCircle + Subfacetten · produktive Referenzverträge

**Produktiver CLS-Stand:** Der aktuell geprüfte CLS-Pointer wird ausschließlich aus `CURRENT_POINTER.json` gelesen. Diese README ist eine Architektur- und Continuity-Referenz, kein eigenständiger Live-Pointer.

Main LiveCircle validiert zuerst die native 666CLS-Authority und den Release mit Prüfsummen. Die fünf Subfacetten behalten ihre eigenen `LIVECIRCLE.json`- und `UI.json`-Dateien. Ihr Status ist `REFERENCE_ONLY`: keine neuen autonomen Trigger, kein Autoload, keine Schreibrechte, keine fremde native Ausführung. Der intelligente Begleit-Daemon gibt nur auf Anfrage Empfehlungen ab.

**666CURES:** CLS katalogisiert v0.2.0 als lokalen Freeze. Die produktive Native Authority liegt weiterhin bei 666PFS (`666PFS-CURES-001`, Entry `CURES-16001`). PFS meldet `HOLD_FUNCTIONAL_PAYLOAD_SOURCE_NOT_FOUND`; der funktionale Payload ist dort nicht als produktive Repo-Runtime verifiziert. Der CLS-Eintrag darf diesen HOLD-Zustand weder überschreiben noch die lokale Sicherung als PFS-Release behandeln.

**Letzter geprüfter CURES-Metadaten-Readback:** 666PFS_CSM/main @ `08989d5dc71259cbebf108c71d2e315aa9ac28a1` mit unveränderten CURES-Identitäts-/Rehydrations-Blobs; PFS-HOLD bleibt. Dieser festgehaltene Commit ist eine zeitgebundene Belegreferenz und muss vor jeder Folgebewertung frisch gelesen werden. Die weitere Arbeit umfasst die nicht verifizierten Originalquellen/Authority-Versionen eigenständiger Kandidaten und den funktionalen CURES-Payload; ausschließlich 666PFS kann eine Native-Owner-Promotion autorisieren. Keine CLS-Registry-Referenz oder README-Angabe ändert eine fremde Authority.
