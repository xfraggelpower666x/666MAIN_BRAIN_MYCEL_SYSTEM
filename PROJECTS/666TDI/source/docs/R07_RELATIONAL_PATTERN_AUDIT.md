# 666TDI v2.5 — R0.7 Relational Music Pattern Integration & Audit

## Arbeitsbasis
- Current: 666TDI v2.5 R0.6 lokale ZIP und entpackte Arbeitskopie, unverändert im Ausgang.
- Scope: **nur lokale, additive Erweiterung** `engine/pattern_relations.py`, `engine/pattern_cli.py` und 12 Tests; README und Modulregistry ergänzt.
- Quellen: `registry/r06_music_candidates.json` (10 historische V5-Pattern-Kandidaten, 3 Presets), `engine/relational.py` (R0.5), `engine/source_adapters.py` (R0.6).
- Identität: `666TDI-001`, **666TDI er/ihn/ihm**. LYVRA ist historische Evidenz, keine Authority.

## Fachliche Umsetzung
1. Der aktuelle Track-Graph wird als maßgeblicher lokaler Kontext gelesen; `assess` ist read-only.
2. Für jede Pattern-Eigenschaft sind musikalische Funktionshypothesen, Kontextevidenz und mögliche Risikokanten hinterlegt.
3. Explizite Zeugen sind Graphknoten/Trackfelder, inklusive Herkunft; fehlende Stützung bleibt sichtbar.
4. Gegenrelationen (z.B. repetitiver Loop bei angeforderter Variation, starker Drop ohne vorbereitenden Kontrast, Stimm-Layer-Masking) werden als **Risiko**, nie als bestätigter Hörfehler ausgegeben.
5. Bereits vorhandene `CONFLICTS`-Kanten des Trackgraphen werden mitgeführt.
6. Kein Ranking als universeller Qualitätsscore; kein automatisches Pattern-Preset und keine Veränderung der musikalischen Entscheidungsautorität.
7. Nur das separate explizite `attach-reviewed` kann einen begründeten Pattern-Bezug lokal im Graphen vermerken. Ungestützte Funktionszuordnungen werden abgewiesen.

## Regression & Grenzen
- 57 Vorgängertests plus 12 spezifische Tests = 69 grün (lokale Python-Standardbibliothek).
- Keine Remote-Verbindung, keine kostenpflichtigen Audiotests, keine GitHub-Writes.
- Der semantische Adapter bleibt **heuristisch**. Er misst weder Frequenzen noch menschliche Bedeutung und darf keine echten Renderer-Ergebnisse behaupten.
- Tracklokale Kandidaten-Annotationen sind keine globalen Lernregeln. Renderer-Feedback aus `relational.py` bleibt separat und benötigt vorhandene Evidenz-/Review-Gates.

## Offene Entwicklung
- Tieferer Abgleich zwischen Ergebnis-Feedback und expliziter Pattern-Funktion mit echten Audio-/Stem-Belegen.
- Stärkere semantische Disambiguierung bei Negationen und metaphorischem Vokabular; derzeit können Begriffe aus `avoid` in den Zeugenkontext einfließen.
- Versionierte Regeländerungen für Heuristiken und kontrolliertes A/B-Labor.

## Nächste sinnvolle Recherchepunkte
1. Audiosignal-gestützte Motor- und Drop-Evaluation.
2. Empirische Gegenbelege für Pattern-Relationen.
3. Renderer-spezifische Adaptionshistorie ohne Genre-Drift.
