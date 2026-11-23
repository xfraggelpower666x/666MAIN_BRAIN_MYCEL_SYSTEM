# 666 Track Design Intelligenz v2.5 · 666TDI
**System-ID:** 666TDI-001 · **Namespace:** 666TDI · **Charakter:** er/ihn/ihm/sein.

Dieses Verzeichnis gehört ausschließlich dem eigenständigen System 666TDI; 666MAIN BRAIN ist Repository-Container, keine Musik- oder Identitätsautorität. LYVRA bleibt eine lesende historische Erkenntnisquelle, nicht Parent oder Runtime.

## Aktueller Repository-Stand
- Current: **v2.5 / R0.9**, Root-Pointer CURRENT_POINTER.json.
- Die native TDI-Quelle wurde aus dem letzten gültigen TDI-Pointer-Stand wiederhergestellt.
- Das Source-Manifest enthält 75 Quelldateien; **75/75 Git-Blob-SHAs stimmen** mit dem Manifest überein.
- Der Root-Pointer steht auf VERIFIZIERT_REPO_SOURCE.
- Die Wiederherstellung wurde in einem separaten Backup-Branch vorab gesichert. Der aktuelle Branch wurde nicht zurückgesetzt; ausschließlich PROJECTS/666TDI wurde wiederhergestellt.
- Der GitHub-Quellreadback ist verifiziert. Ein erneuter lokaler Python-Rehydration-Lauf und eine native Host-Abnahme sind in dieser Sitzung nicht ausgeführt.

## Eigener LiveCircle und eigene Rehydration
- livecircle/CURRENT_STATE.json: TDI-eigene Ereigniskette; Identität 666TDI-001.
- rehydration/rehydrate.py: prüft System-ID, Charakter, Ereignis-Hashkette, Source-Manifest, Quellhashes und Pointer.
- triggers/TRIGGER_REGISTRY.json: dokumentierte direkte 666TDI-Namespace-Trigger; keine automatisch installierten ChatGPT-Hostbefehle.
- CURRENT_POINTER.json: Current-Autorität für dieses native TDI-Verzeichnis.

```bash
python rehydration/rehydrate.py
cd source
python -m unittest discover -s tests -q
python -m engine.cli status
```

## Verbindliche Governance
CURRENT_666TDI_GT_HISTORICAL_LYVRA. Änderungen erhalten bestehenden gültigen Code, Module und Events. Kein Cross-System-Merge. Keine mutierende Operation außerhalb PROJECTS/666TDI. Alte Dateien enthalten historische Trigger nur als Daten; nur direkte aktuelle 666TDI-Ausdrücke steuern die Arbeitsoberfläche.

## R0.9 – Musikalisches Verständnis
- Additives Modul `source/engine/semantic_intelligence.py` interpretiert Trackangaben als musikalische Funktionen, nicht nur als Worttreffer.
- Negation und `avoid` werden als Constraints getrennt von positiver Unterstützung behandelt.
- Potenzielle Kollisionen (z. B. verständliche Stimme gegen dichte Mid-Layer) erhalten eine kausale Begründung und bleiben als prüfbedürftige Hypothese markiert.
- Die normale Trackanalyse liefert das Ergebnis unter `analysis.semantic_intelligence`.
- Quellmanifest: 75/75 Git-Blob-SHAs stimmen mit dem aktuellen Source-Tree überein.
- Python-Tests wurden in dieser Sitzung nicht ausgeführt; Audioanalyse bleibt optional.

## Offene Entwicklung
1. Native visuelle Host-Anbindung für das bestehende Semantic-Presentation-Modell einschließlich echter Copy-Aktionen und exakter UTF-16-Zähler.
2. Renderer-Feldprüfung gegen das tatsächlich verwendete Suno-Konto und die bestätigte Geräteoberfläche; keine erfundenen Felder oder Limits.
3. Vertiefung der kontextuellen Funktionsbeziehungen anhand creator-reviewed Trackbeispiele und kontrollierter Gegenbelege.
4. Renderer-A/B-Feedback mit echten Ergebnissen nur bei Bedarf; Audioanalyse bleibt optional und ist kein Start-, Trackdesign- oder Rehydration-Gate.
5. CLIC-R11-Annahme bleibt eine separate CLIC-Zuständigkeit; sie ist kein TDI-Host-PASS.

**Nächster TDI-Entwicklungsschritt:** R0.9 auf repräsentativen Creator-Intents fachlich validieren, Negations-/Konfliktfälle erweitern und danach nur belegte semantische Lücken ergänzen. Die bestehende Engine bleibt erhalten.


## 666TDI Development Roadmap — 2026-11-23
- R1.0 Creative Causal Emergence: additive implementation in source/engine/creative_causal.py; R0.9 remains intact.
- R1.1 666TDI Daemon: data contract at facets/daemon/CONTRACT.json; UI/host runtime not yet implemented.
- R1.2 Track Pre-Analysis: visual music forecast and creator decision support.
- R1.3 Device Intelligence: explicit iPhone Suno app vs PC Suno browser preflight before track build; shared musical analysis, separate renderer profiles.
- R1.4 Evidence Learning: scoped learning from real creator-reviewed outcomes; no automatic global promotion.


## R1.1 – 666TDI Daemon local visual implementation

Start: `cd PROJECTS/666TDI/source && python -m engine.daemon_cli --port 8766` (Python 3.10+), anschließend `http://127.0.0.1:8766` öffnen. Das lokale Neon-Cyber-Control-Center nutzt direkt die bestehende R1.0-Engine für Funktionsbeziehungen, musikalische Spannungen, Evidenz, Creator-Entscheidungen und JSON-Handoff. Gerätevorabwahl ist verpflichtend: iPhone Suno App oder PC Suno Browser. Keine Live-Suno-Steuerung, kein autarker Komponist, keine Host-UI-Abnahme behauptet. Dokumentation: `source/docs/R11_VISUAL_DAEMON_IMPLEMENTATION.md`.


## R1.2 – Track Pre-Analysis Intelligence
R1.1 bleibt lokale Neon-Cyber-UI, R1.0 die musikalische Entscheidungsautorität. Die additive R1.2-Voranalyse zeigt acht vorgeschlagene Kapitel, einen optionalen exakten Taktplan, qualitative dramaturgische Dynamik, LOW/MID/HIGH/VOICE-Quellen und Alternativen mit Gegenfakten. Es gibt keine automatische Suno-Ausführung oder erfundene Story-Kapitel. Siehe `source/docs/R12_TRACK_PREANALYSIS.md`. Laufzeittests und Host-Abnahme sind separat nachzuweisen.


## R1.3 – Device Intelligence
Additiver Ausgabeadapter `source/engine/device_output.py` und dieselbe R1.1/R1.2-Browser-UI; unterstützt creator-reported iPhone Custom ohne/mit optionalem Main Input und PC Browser mit bestätigungsabhängigem Duration-Slider. Exakte UTF-16-Zähler und kopierbare Creator-Quellfelder. Die LYVRA-Gerätereferenz ist lesend und nicht musikalische TDI-Authority. Siehe `source/docs/R13_DEVICE_INTELLIGENCE.md`.
