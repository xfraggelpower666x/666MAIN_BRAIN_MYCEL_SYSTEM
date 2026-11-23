---
name: sceeri-quality-gates
description: Use for bounded quality gates, code safety, static checks, regression test selection and readback of proposed Python, Java and web changes.
---

# Quality Gates & Recovery

Prüfe zuerst sichtbare Quellen, Diff und vorhandene Ergebnisse. Trenne Syntax, statische Typ- und Stilprüfung, Java-Kompilierung, Browserverhalten und fachliche Regression. Führe Tests nur in einer passenden, autorisierten Umgebung aus. Ohne sie liefere Eingaben, erwartetes Ergebnis und Prüfplan. Dokumentiere Basis, Diff und Recovery-Beleg. Bei Regression halte den Konflikt fest und prüfe die Rückkehr auf einen bestätigten Ausgangsstand. Verwende das [Chat-Betriebsmodell](../../references/chat-betriebsmodell.md).

Die [Freigabekriterien des Engineering-Zyklus](../../references/engineering-zyklus.md#freeze) legen fest, wann ein Paket geprüft ist und wann ein Host-Nachweis offen bleibt.
