# 666 RESEARCH MD DATABASE ORCHESTRA — Live-System / Recovery Worktree

**Arbeitsstand:** `PARTIAL · READBACK_PENDING` (22.11.2026). **Kein neuer Freeze und kein vollständiger v1.7.1-Rebuild.**

Dies ist das dauerhaft bearbeitbare GitHub-Projekt unter `PROJECTS/666_RESEARCH_MD_DATABASE_ORCHESTRA/` auf Branch `666MAIN_BRAIN`. Der Projektordner ist von 666CLS, LYVRA, 666PFS, 666CLIC und anderen Systemen isoliert. Das Host-Repository ist kein Authority-Transfer.

## Sofort nutzbarer Einstieg

```bash
python3 tools/livecircle.py status
python3 tools/livecircle.py audit --json
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s recovery/tests -v
```

Der Status-CLI ist lesend und kann den unvollständigen Source-Readback nicht als PASS darstellen. `audit` beendet sich bei fehlenden Originalen mit Code 2.

## Wiederherstellung weiterer Originalquellen

1. Einen **belegten Original-Quellstand** als Verzeichnis oder ZIP bereitstellen (niemals ins Git-Repo als Archiv einchecken).
2. Quelldateien mit `python3 recovery/tools/source_readback_guard.py --source <QUELLORDNER_ODER_ZIP> --sha-manifest history/v1_7_1/SYSTEM_ONLY_FILE_MANIFEST_SHA256.txt` auf den Vollstand prüfen.
3. Teilfunde einzeln durch SHA-256-Abgleich gegen das historische Manifest verifizieren, dann ausschließlich im ursprünglichen Pfad ergänzen. Bereits verifizierte Dateien nicht überschreiben.
4. Nach vollständigem Readback Originaltests ausführen. Erst danach neue Release- und Freeze-Evidenz schreiben.

## Struktur

- `data/topics/` und `data/prompts/` — **3 SHA-256-genau zum v1.7.1-Manifest passende Originaldateien**, noch nicht als lauffähiges v1.7.1-System aktiviert
- `history/v1_7_1/` — vergangene Audit-, Freeze- und Manifestdokumentation, nicht neue Authority
- `recovery/tools/` und `recovery/tests/` — original erhaltenes, isoliertes Guard-Werkzeug mit Regression
- `tools/livecircle.py` — lesender Live-Arbeitsstand, Inventar, nächste Schritte
- `state/LIVE_WORKSPACE_STATE.json` — der fortsetzbare Recovery-Zustand
- `tests/` — zusätzliche LiveCircle-Regression

**Ausschluss:** keine generierten Texte, Lyrics, Bilder, Audio, PDFs/DOCX, Ergebnisse, Suchhistorien, Credentials, User-Stems oder temporären Dateien einchecken. `history/` speichert ausschließlich notwendige Release-Metadaten, nicht einen Suchverlauf.
