# 666TDI v2.5 — R0.8 Causal Audio Feedback Audit

## Autorität und Erhalt
- 666TDI-001 bleibt alleinige lokale Musiksystem-Identität, Charakter er/ihn.
- R0.7 ist die gültige Vorgängerbasis; R0.8 ergänzt ohne Ersatz der vorherigen Engine.
- Neue Dateien: `engine/audio_feedback.py`, `engine/audio_cli.py`, `tests/test_audio_feedback.py`.
- Bestehende README und Modulregistry erweitert; alle anderen Vorgängerdateien bytegleich.
- Keinerlei externe Repository- oder Provider-Writes.

## Tatsächlich messbar
- SHA-256 der gelieferten Audiodatei, Dateilänge, Abtastrate, Kanäle, Dauer.
- Sample-Peak, ungewichteter RMS, Crest Factor, 100-ms-RMS-Zeitfenster, stillenähnliche Fenster unter -60 dBFS.
- FFT-basierte Bandenergie für LOW / MID / HIGH; für zwei Stems ein grober Energieüberlappungsindikator.
- Quantitativer Vergleich der geplanten und tatsächlich gemessenen Dauer. Optionales strukturiertes Evidenz- und Review-Ledger.

## Nicht behauptet
- Kein psychoakustisch gesichertes Masking, keine echte Gesangsverständlichkeit, keine sichere BPM-/Tonarterkennung.
- Kein True Peak, kein EBU R128 LUFS, kein reproduzierter Studio-Mix.
- Kein Anbieter-Render und keine individuelle Ursache aus einer Messung ableitbar.
- Reviewer-Angaben sind überprüfbare Dateneinträge, aber **nicht selbst** eine unabhängige Validierung.
- Keine automatische Regelpromotion, kein Lernen ohne belegte Vergleichstests, keine falschen Aussagen über Audio ohne echte Datei.

## Nachweise
- `python -m unittest discover -s tests -q`: 84 Tests erfolgreich (69 vorherige plus 15 neue).
- Test-fixtures: selbst erzeugte Sinus-WAVs im temporären Verzeichnis, nicht reale Suno- oder ACE-Step-Ausgaben.
- Audio-CLI verifiziert mit synthetischer Datei, echte Nutzeraudio-Validierung noch OFFEN.

## Risiken / offene Weiterentwicklung
- Audioanalyse liest die gesamte Datei in den RAM; 350 MiB Dateigrößengrenze und 30-min Limit. Für sehr große Stems Streaming ausbauen.
- FFT-Energieanteile messen Signalverteilung, nicht hörbare Konkurrenz; Stereo-Korrelation ist nur ein grober Indikator.
- Wahrnehmungs- und Ursachebewertung braucht gemessene A/B-Varianten und explizite Review-Evidenz.
- Die Audio-Evidenz liegt in eigenen Dateien; zentrale Ereigniskette wird bewusst nicht still geändert. Lifecycle-/Handoff-Anbindung ist ein zukünftiger kontrollierter Schritt.

## Status
VERIFIZIERT_LOCAL_STRUCTURE · AUDIO_TEST_SYNTHETIC_VERIFIED · REAL_RENDER_VALIDATION_OFFEN · NO_AUTO_PROMOTION.
