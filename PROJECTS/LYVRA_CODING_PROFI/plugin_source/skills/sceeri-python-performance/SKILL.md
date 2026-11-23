---
name: sceeri-python-performance
description: Locate Python bottlenecks and compare baseline and candidate using equivalent workloads, repeated measurements, and a correctness check.
---

# Python-Profiling und Benchmarking

Verwende diesen Ablauf bei langsamen Python-Abläufen oder messbaren Optimierungszielen. Nutze [Python-Projektprüfungen](../sceeri-python-project-checks/SKILL.md) für unverändertes Verhalten.

1. Wähle den realen Einstiegspunkt und eine repräsentative Eingabe. Halte Revisionen, Python-Version, Abhängigkeiten, Eingabegröße, Cache-Zustand und Messziel fest. Trenne Startzeit, Verarbeitungszeit und Durchsatz. Bei Speicherbedarf unterscheide Python-Allokationen von Prozessspeicher.
2. Prüfe die fachliche Ergebnisgleichheit beider Stände. Vergleiche Rückgabewerte und vereinbarte Seiteneffekte mit demselben Test. Nutze eine vereinbarte Toleranz für Gleitkommazahlen.
3. Lokalisiere den Engpass anhand eines vorliegenden oder autorisiert gemessenen Funktionsprofils oder eines Berichts zu Speicherallokationen. Ohne Profil liefere eine Hypothese und einen Messplan. Berichte Profiling getrennt von Zeitmessungen, da Instrumentierung die Zeiten verändert.
4. Vergleiche Baseline und Kandidat ohne Profiling in gleichwertigen isolierten Umgebungen. Verwende identische Daten, dokumentierte Aufwärmläufe und wiederholte Messungen. Für ein kurzes isoliertes Snippet ist `timeit` geeignet. Wechsle bei Vergleichsläufen die Reihenfolge, wenn Drift durch Last oder Erwärmung relevant ist.
5. Berichte Anzahl, Median, Streuung und Einheit, zusätzlich zur absoluten und prozentualen Änderung gegenüber der Baseline. Wenn die Schwankung den Unterschied überdeckt, markiere den Geschwindigkeitsgewinn als offen. Prüfe einen relevanten Randfall und mögliche Kosten in Speicher oder Wartbarkeit.

**Abnahme:** Beobachtete Messwerte je Stand, gleiche Ausgaben und ein nachvollziehbarer Vergleich. Ein plausibler Engpass ohne Messung bleibt `ABGELEITET`.
