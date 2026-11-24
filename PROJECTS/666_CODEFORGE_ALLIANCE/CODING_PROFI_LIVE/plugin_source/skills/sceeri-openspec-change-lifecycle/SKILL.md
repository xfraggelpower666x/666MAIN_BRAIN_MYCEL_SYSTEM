---
name: sceeri-openspec-change-lifecycle
description: "Führt OpenSpec-Vorschlag, beauftragte Umsetzung und Archivierung im Chat mit Spec-Deltas, Aufgaben und Evidenz."
---


# OpenSpec-Änderungsablauf

Wähle die Phase nach Auftrag. Ermittle Projekt, tatsächlich verwendete OpenSpec-Konventionen, Change-ID und vorhandene Specs, Vorschläge und Aufgaben aus den lesbaren Quellen. Bei mehrdeutiger Change-ID löse den Konflikt vor Änderungen auf. Sichte projektspezifische Anleitungen im vereinbarten Scope.

## Vorschlag

Entwirf eine eindeutige, handlungsorientierte Change-ID und einen Vorschlag mit Anlass, Umfang, Auswirkungen und Akzeptanzkriterien. Ergänze eine geordnete Aufgabenliste und bei wesentlichen Entwurfsentscheidungen ein Design. Formuliere Deltas je Capability für hinzugefügte, geänderte oder entfernte Anforderungen. Gib jeder Anforderung mindestens ein überprüfbares Szenario. Verknüpfe gemeinsame Verträge und Aufgabenabhängigkeiten. Liefere Dokumententwürfe und prüfe ihre Konsistenz. Strikte CLI-Validierung gilt als ausgeführt, wenn ihr Ergebnis für diese Change-ID beobachtet wurde.

## Umsetzen

Lies den beauftragten Vorschlag, Design, Deltas und Aufgaben. Verbinde jede Änderung mit einem Szenario und dem kleinsten passenden Diff. Arbeite nach Abhängigkeiten. Führe vorhandene Prüfungen im autorisierten Host aus, wenn verfügbar. Markiere eine Aufgabe abgeschlossen, sobald ihr tatsächliches Ergebnis belegt ist. Bei widersprüchlichem Ist-Stand kläre Umfang und Vertrag vor der betroffenen Änderung.

## Archivieren

Bestätige eindeutige Change-ID, Abschluss und erforderlichen Auslieferungsbeleg. Prüfe bestehendes Archiv und die erwarteten Auswirkungen der Deltas auf den aktuellen Spec-Stand. Bei reinem Tooling kann die projektspezifische Archivierung ohne Spec-Änderung vorgesehen sein. Liefere im Chat Archivplan oder Review. Bei konkret beauftragter und verfügbarer Host-Ausführung lies Archivziel und resultierende Specs zurück und protokolliere die strikte Validierung. Ein Entwurf oder ein sichtbarer Ordner allein belegt keinen erfolgreichen Abschluss.
