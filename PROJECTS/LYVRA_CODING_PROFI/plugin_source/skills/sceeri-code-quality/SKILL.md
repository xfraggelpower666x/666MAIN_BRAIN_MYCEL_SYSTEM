---
name: sceeri-code-quality
description: "Prüft Python-Qualitätskonfiguration, Ruff, Typprüfung, pre-commit und Dokumentationsprüfungen."
---


# Python-Qualität

Ermittle geltende Python-Version, Formatierung, Lint, Typprüfung, CI und Hook-Konfiguration. Verwende die vorhandenen Befehle und Regeln. Bei fehlendem Setup schlage eine kleine Ruff-Konfiguration und passende Hygiene-Checks vor. Dazu zählen whitespace, Dateienden, YAML/TOML-Prüfung und Schutz vor versehentlich eingecheckten Geheimnissen. Behandle Formatierungsänderungen separat von fachlichen Diffs.

Prüfe bei Bedarf README, Markdown-Links, veröffentlichte Docstrings und die Übereinstimmung lokaler Checks mit CI. Berichte pro Prüfung belegten Lauf oder offene Voraussetzungen. Neue Hooks, Tools und Abhängigkeiten benötigen einen fachlichen Grund. Bestehende Ausnahmen gezielt verstehen, bevor du sie änderst.
