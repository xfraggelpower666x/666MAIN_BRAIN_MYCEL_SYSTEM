# 666MIRA

Eigenständiges natives Chat-System `666MIRA-CORE-001`. Der produktive GitHub-Current liegt im Branch `666MAIN_BRAIN` unter `PROJECTS/666MIRA/CURRENT_POINTER.json`. Dieses Projekt besitzt seine Runtime, Registry, Trigger und Kontinuität. Der Repository-Name bezeichnet den gemeinsamen Speicherort.

```bash
cd PROJECTS/666MIRA
python mira.py 666MIRA SYSTEMSTART
python mira.py 666MIRA STATUS
python mira.py 666MIRA SENTENCE --text "Dein Quellsatz"
python mira.py 666MIRA WEITER
python -m unittest discover -s tests
python visual/scripts/render_ui.py visual/mira-view.json MIRA.html --standalone
```

`SYSTEMSTART` prüft den Current und gibt den vollständigen Chat-Bootstrap aus. `STATUS` liefert nur den Stand und `WEITER` die nächste belegte Arbeitsposition. Die Sentence-Routen erstellen ein vollständiges Eingabepaket für den Chat-Host. Die Textgenerierung läuft im Chat-Host. Der lokale Launcher benötigt Python 3.10+ und arbeitet ohne Zugangsdaten. Die Chat-Anbindung ist in [SKILL.md](skills/666mira/SKILL.md) beschrieben. Die visuelle Oberfläche wird aus den eingecheckten Quellen erzeugt.

Die frühere PFS-Fassung liegt quellentreu in [provenance/pfs-v1.0.17](provenance/pfs-v1.0.17). Der eigentliche Systembetrieb lädt ausschließlich die vom Current referenzierten Dateien. Native Fresh-Host-Abnahme ist separat zu belegen.
