# 666 Track Design Intelligenz v2.5 · 666TDI
**System-ID:** 666TDI-001 · **Namespace:** 666TDI · **Charakter:** er/ihn/ihm/sein.

Dieses Verzeichnis gehört ausschließlich dem eigenständigen System 666TDI; 666MAIN BRAIN ist nur Repository-Container und keine Musik- oder Identitätsautorität. LYVRA bleibt eine lesende historische Erkenntnisquelle, nicht Parent oder Runtime.

## GitHub-Übertragungszustand: READBACK_PENDING
Das lokale R0.8-Paket ist validiert (84/84 Tests, 79 ZIP-Dateien); 71 für das öffentliche Repository geeignete Quelldateien müssen noch unter `source/` übertragen werden. 8 historische/quellbezogene Dateien sind zunächst wegen des öffentlichen Repositories vom Transfer ausgeschlossen; sie bleiben in der lokalen Originalsystemsicherung. **Kein vollständiger GitHub-Systemstart behauptet.**

## Eigener LiveCircle und eigene Rehydration
- `livecircle/CURRENT_STATE.json`: aus der lokalen R0.8-Kette übernommene Ereignisse; Identität 666TDI-001.
- `rehydration/rehydrate.py`: überprüft System-ID, Charakter, Ereignis-Hashkette, Source-Manifest, Quellhashes, Pointer.
- `triggers/TRIGGER_REGISTRY.json`: dokumentierte 666TDI-Namespace-Trigger, keine automatisch installierten ChatGPT-Hostbefehle.
- `CURRENT_POINTER.json`: **nur nach vollständigem Repository-Readback** auf `VERIFIZIERT_REPO_SOURCE` setzen.

```bash
python rehydration/rehydrate.py
# nach vollständigem Import:
cd source
python -m unittest discover -s tests -q
python -m engine.cli status
```

## Verbindliche Governance
CURRENT_666TDI_GT_HISTORICAL_LYVRA. Alle Änderungen erhalten bestehenden gültigen Code, Module und Events. Kein Cross-System-Merge. Keine mutierende Operation außerhalb `PROJECTS/666TDI`. Alte Dateien enthalten lediglich historische Trigger als Daten; nur neue direkte 666TDI-Ausdrücke steuern die Arbeitsoberfläche.

**Beleg:** Lokaler Archiv-SHA256 `4f0741ef3fdf438772fda6d406baaca02eddd4262ef9681bdc2517955c1703d1`. Der GitHub-Source-Readback bleibt offen, solange `source/` unvollständig ist.
