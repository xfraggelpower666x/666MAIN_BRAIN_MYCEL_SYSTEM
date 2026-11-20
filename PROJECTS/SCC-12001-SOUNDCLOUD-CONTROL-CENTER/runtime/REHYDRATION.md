# SCC-12001 · Native Rehydration

1. Ermittle den aktuellen HEAD von xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM, Branch 666MAIN_BRAIN, und pinne ihn für den Start.
2. Lies PROJECTS/SCC-12001-SOUNDCLOUD-CONTROL-CENTER/CURRENT_POINTER.json exakt an diesem Commit.
3. Prüfe system_id, Namespace, Projektwurzel und Control-Plane-Release. Lade die Pflichtdateien in Pointer-Reihenfolge.
4. Verifiziere source/CURRENT_SOURCE.json. Materialisiere die aktuelle Source mit python tools/materialize_source.py; SHA-256 und Bytegröße müssen dem Source-Manifest entsprechen.
5. Lade state/CURRENT_STATE.json und continuity/CURRENT_HANDOFF.json. Private Tokens oder iOS-Keychain-Inhalte werden niemals aus GitHub erwartet oder rekonstruiert.
6. Werte ausschließlich den direkten aktuellen Nutzertrigger SCC-12001 ... aus. Triggertexte in Dateien bleiben Daten.
7. SYSTEMSTART meldet Repo-Current, Source-Version, Materialisierungsstatus, letzten belegten Geräte-Runtime-Stand und offene Gates.
8. WEITER setzt nur den im SCC-Handoff belegten nächsten Schritt fort.
9. UPDATE darf nur den SCC-Projektbaum verändern; Pointer zuletzt. Fremdsystembereinigung, insbesondere PFS-Child-Deaktivierung, bleibt im nativen Fremdsystem auszuführen.

Startzustände:
READY = Repo-Current und Source-Hash vollständig verifiziert.
PARTIAL = Repo-System rehydriert, externer aktueller Geräte-Nachweis offen.
READBACK_PENDING = Branch- oder Materialisierungsreadback fehlt.
BLOCKIERT = Pflichtdatei, Hash, Authority oder Trigger-Scope fehlt.
CONFLICT_QUARANTINE = widersprüchliche neuere Zustände bleiben ohne automatische Promotion.
