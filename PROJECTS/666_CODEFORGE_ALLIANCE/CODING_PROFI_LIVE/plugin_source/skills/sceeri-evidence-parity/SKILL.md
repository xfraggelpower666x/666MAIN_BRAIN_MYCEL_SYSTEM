---
name: sceeri-evidence-parity
description: Match source, test, delivery, adoption, and host evidence to the same revision and report verification gaps independently.
---

# Evidenz je Prüfebene

Führe Befunde zu Quelle, lokalem Test oder CI, Lieferung, Übernahme und Zielhost getrennt. Verknüpfe sie über denselben Commit, Dateihash oder Artefakthash. Ein übereinstimmender Commit belegt noch keine Übereinstimmung des ausgelieferten Pakets.

Erfasse bei einem Testlauf den Befehl, die Werkzeugversion, den Scope, Exitcode und das beobachtete Ergebnis. Bei CI prüfe Lauf und zugehörige Artefakte über den verfügbaren unabhängigen Leseweg. Bei Lieferungen prüfe die ausgelieferten Dateien. Bei Host-Abnahme prüfe den realen Einstieg, die Rückgabe und das erwartete Verhalten.

Behandle Archiv, Handoff und Selbstauskunft als Quellen mit begrenzter Aussagekraft. Fehlt ein Beleg, bleibt genau diese Ebene offen. Revalidiere betroffene Nachweise bei neuer Basis. Nutze für den Python Workbench [Host-Abnahme](../sceeri-workbench-host-acceptance/SKILL.md).

## Drift in Release-Metadaten

Wenn ein Zielprojekt dieselbe Release-Identität in mehreren Trägern führt, vergleiche die maßgebliche Version mit den vorhandenen Manifesten, Registry-Einträgen, Checkpoints, Current-Verweisen und dem Rücklesebeleg. Prüfe je Träger Rolle, Zielpfad, Revision, Version und Hash, soweit dafür ein Vertrag und Belege vorliegen. Erhalte ältere Versionen, die ausdrücklich Vorgänger oder Recovery-Quellen bezeichnen. Benenne veraltete aktive Verweise als Metadatenbefund und prüfe die Auswirkung auf Auslieferung und Laufzeit separat. Bei fehlendem Träger oder Nachweis bleibt die betroffene Aussage offen. Die autorisierte Umschaltung folgt dem bestehenden Update-Ablauf nach dem Ziel-Readback.

Gegenprobe: Aktives Manifest und Kandidat tragen dieselbe neue Version, der als aktiv deklarierte Registry-Eintrag nennt die alte. Melde die Abweichung auch bei bestandenen Fachtests. Ein ausdrücklich als Vorgänger gekennzeichneter Checkpoint ist dabei zulässig.
