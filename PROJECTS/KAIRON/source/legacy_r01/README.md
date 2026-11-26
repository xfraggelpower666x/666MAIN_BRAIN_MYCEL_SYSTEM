# Lokale Musikarchitektur — unabhängiger Prototyp R0.1

**Status: LOCAL_PROTOTYPE / NO_REPO_WRITE / AUDIO_UNVERIFIED**

Ein eigenständiger Python-Compiler für ein musikalisches Intent-Objekt mit rendererbezogenen Feldgrenzen, Prioritätsabgleich und sichtbarer Semantik-Verlustmeldung. Quelle ist eine lesende Analyse vorhandener LYVRA-Musikintelligenz plus historischer ASG-Renderer-Recherche. Keine LYVRA-Datei wird modifiziert oder hier als Ausführungsquelle eingebunden.

## Ausführen
```bash
python src/music_arch.py examples/intent.json lyria2_asg
python -m unittest discover -s tests -v
```

Renderer-IDs: `asg_main`, `ace_step_asg`, `lyria2_asg`, `elevenlabs_asg`, `suno_reference`.

**Nicht vorhanden:** echte Renderer-API-Aufrufe, Audio-Rendering, persistentes Lernsystem, Live-Feldverifikation, vollständiges Track-Arrangement oder Produktionsreife. Die bewusste Meldung von Informationsverlust ist kein behobener Funktionsverlust.
