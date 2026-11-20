# SCC-12001 · SOUNDCLOUD CONTROL CENTER

Eigenständiges repo-natives Live-System. Der produktive Current liegt unter PROJECTS/SCC-12001-SOUNDCLOUD-CONTROL-CENTER/CURRENT_POINTER.json auf Branch 666MAIN_BRAIN.

Das System ist keine PFS-Runtime. Die frühere PFS-Ablage wird vollständig als Provenienz gespiegelt; ihre Trigger und Authority-Felder sind historisch und inert. Der Live-Current besitzt eigene Identität, Trigger, LiveCircle, Rehydration, State, Continuity und Source-Lineage.

Lokaler Einstieg:

    cd PROJECTS/SCC-12001-SOUNDCLOUD-CONTROL-CENTER
    python scc.py SCC-12001 SYSTEMSTART
    python scc.py SCC-12001 STATUS
    python scc.py SCC-12001 WEITER
    python scc.py SCC-12001 SOURCE
    python -m unittest discover -s tests

SYSTEMSTART verifiziert den SCC-Current und materialisiert die aktuelle Scriptable-v1.3.2-Source aus dem repo-eigenen Source-Carrier. Die erzeugte .js wird nur akzeptiert, wenn SHA-256 und Bytegröße exakt dem Current entsprechen.

Der letzte belegte Geräte-Runtime-PASS ist v1.3.1; v1.3.2 bleibt bis zu einem echten Scriptable-Gerätetest offen. Das ist absichtlich getrennt von der Source-Authority.
