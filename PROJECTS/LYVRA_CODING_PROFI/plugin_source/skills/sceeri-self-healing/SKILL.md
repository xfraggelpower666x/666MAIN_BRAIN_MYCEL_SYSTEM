---
name: sceeri-self-healing
description: Diagnose and stage bounded, reversible repairs with authorization, prechange backup, regression tests and postchange readback.
---

# sceeri-self-healing

1. DETECT: gather concrete failures and reliable baseline. If symptoms are unverified, diagnose read-only.
2. ISOLATE: constrain scope to a single confirmed cause or smallest safe patch; preserve all unrequested structure.
3. PLAN: include write permission, correct native authority, target, lock/version, expected diff, blast radius, backup and rollback strategy.
4. GATE: no protected write without direct owner authorization; no credential exposure, chargeable services or cross-system mutation.
5. APPLY only if tools and authorization actually permit. Retry transient failures at most three times with delay where runtime supports it; do not blindly retry non-idempotent writes.
6. VERIFY: independent body readback, dedicated tests, regression checks, and host acceptance where required; never conflate CI success with production acceptance.
7. COMMIT: publish canonical pointer last, and no further mutation after pointer publication within that update. On uncertain writes: READBACK_PENDING, stop and reconcile before retry.
8. ROLLBACK with explicit authority when safe, else CONFLICT_QUARANTINE. If no execution tool: deliver proposed patch with WRITE_BLOCKED, never claim healed.

## Wiederholter Fehler

Wenn dieselbe Gegenprobe am selben relevanten Stand mit demselben Fehler scheitert und der letzte Versuch keine neue Diagnose oder Verbesserung ergibt, halte Befund-ID, Basis, letzten Versuch und beobachtetes Ergebnis fest. Wiederhole denselben Reparaturansatz erst bei einer neuen belastbaren Beobachtung oder einer gezielt anderen Gegenprobe. Unabhängige beauftragte Arbeit kann weiterlaufen. Bei unklarem Schreibausgang hat der bestehende Zielabgleich Vorrang. Zeige den begrenzenden Befund über die [Daemon-Karte](../../references/scevi-visual-contract.md#daemon-karte).

## Kausalprüfung am normalen Einstieg

Verfolge die betroffene Eingabe über den normalen Aufrufpfad bis zum beobachteten Symptom. Halte den ersten belegten Bruch, den erwarteten Vertrag, die tatsächliche Abweichung und die betroffenen Aufrufer fest. Unterscheide bestätigte Ursache, Hypothese und fehlenden Nachweis. Ein nicht verfügbares Prüfwerkzeug begründet zunächst eine Nachweislücke. Eine belegte und beauftragte Verhaltensänderung ist Teil des Solls.

Binde einen beauftragten Repair an diese Ursache und die vorhandenen Freigaben. Prüfe danach mit derselben Eingabe den normalen Aufrufpfad sowie den betroffenen Vertrag. Ein scheinbar korrektes Ergebnis über einen unbeabsichtigten Nebenpfad reicht für die Abnahme des vorgesehenen Einstiegs nicht aus. Bei offener Gegenprobe melde den Teilstand über die Daemon-Karte.

## Reparaturadapter gegen eine neue Basis

Erfasse vor Aktivierung des Reparaturpfads Eingabe, Ausgabe, native Invarianten, beobachtete Abweichung und den erwarteten Effekt am regulären Einstieg. Ein abweichender neuer Stand oder defekter Hostzugriff allein begründet keinen Zieldefekt. Vergleiche den Zielzustand zuerst lesend. Fehlt ein bestätigter Bruch einer weiterhin gültigen Invariante, führe die Diagnose fort. Bei einem bestätigten Defekt verwende bestehende Zielmechanismen mit begrenztem Scope und separatem Nachweis für Body, Rückkehrbasis und Readback.

## Recovery aus dem LiveCircle

- **Eigener Zustand:** Verwende bei veralteter Strang-Evidenz die im [Checkpoint-Abgleich](../../references/checkpoint.md#git-rehydration-mit-auswirkungsprüfung) belegten Änderungspfade. Repariere zuerst die Zuordnung von Beleg, Basis und offenem Schritt. Ersetze einen defekten Zustand durch bestätigte Fakten und aktualisiere abhängige Entscheidungen. Halte die vorige Entscheidung nachvollziehbar.
- **Autorisierte Zielprojekte:** Nehme den ersten bestätigten Vertragsbruch als Reparaturziel. Nutze Zieladapter und vorhandenen normalen Einstieg. Prüfe denselben Fehlerfall, betroffene Verbraucher und den tatsächlichen Zielzustand nach dem Patch. Nimm den Zustand erst nach belegter Gegenprobe wieder in die laufende Linie auf.
- **Unklarer Schreibausgang:** Lese das konkrete Ziel und halte die Wirkung fest. Wiederhole einen Write erst nach gesicherter Entscheidung über den alten Versuch.
- **Neue Zusammenhänge:** Wenn mehrere Änderungen und Symptome eine neue Ursache nahelegen, formuliere die erwartete Beobachtung und prüfe sie gegen eine plausible Alternative. Ein bestätigter Befund kann die Reparatur ändern. Ein bloßer Dateitreffer ändert zunächst nur, welche Prüfung aussteht.
