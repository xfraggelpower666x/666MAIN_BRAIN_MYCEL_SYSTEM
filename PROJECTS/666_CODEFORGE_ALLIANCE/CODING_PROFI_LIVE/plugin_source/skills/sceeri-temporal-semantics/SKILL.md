---
name: sceeri-temporal-semantics
description: "Prüft Zeitsemantik in Python, JavaScript, TypeScript und Systemverträgen bei Kalender-, Zeitzonen- und DST-Fehlern."
---

# Zeitsemantik

1. Ermittle pro Feld Zweck und Vertrag. Klassifiziere Zeitpunkt, Kalendertag, lokale Uhrzeit, zonierten Termin, verstrichene Dauer oder wiederkehrenden Zeitplan. Erfasse IANA-Zone, Offset, Zeitzonenquelle und gespeichertes Format getrennt.
2. Verfolge Eingabe, Parser, Normalisierung, Speicher, API, Berechnung und Anzeige. Prüfe die fachliche Bezugszone am Verbraucher. Unterscheide UTC für Zeitpunkte von lokalen Tagen und Terminen.
3. Prüfe folgende Signale im Kontext. Eine bewusste und belegte Ausnahme bleibt mit Grund sichtbar.

| Herkunfts-ID | Prüfsignal |
| --- | --- |
| JS001, JS002 | Nur-Datum oder Zeitstempel ohne Offset wird als JavaScript-Date interpretiert |
| JS003, JS004 | Kalenderdatum aus UTC-ISO abgeschnitten oder Formatierung von Host-Zone abhängig |
| JS005 | Feste 24-Stunden-Schritte bei fachlicher Kalendertagsrechnung |
| PY001, PY002 | Naive aktuelle Uhrzeit oder naives UTC aus utcnow |
| PY003, PY004 | Timestamp-Umwandlung ohne explizite Zone oder naive UTC-Konvertierung |
| PY005, PY006 | Direkte pytz-Zuweisung oder Wechsel von Metadaten statt Umrechnung eines Zeitpunkts |
| PY007 | Ein Tag oder 24 Stunden, obwohl der nächste lokale Kalendertag gemeint sein kann |

4. Prüfe relevante Grenzfälle. Dazu zählen lokale und UTC-Mitternacht, Monats- und Jahreswechsel, DST-Lücken und doppelte Uhrzeiten, abweichende Host-Zonen, Serialisierung und Datenbank-Roundtrip. Kläre bei Mehrdeutigkeit die fachliche Wahl frühere/spätere Instanz oder Ablehnung. Wähle die Zonen des Projekts.
5. Gib je Befund Fundstelle, Kontext Produktion/Test, Bedeutung, konkreten Grenzfall, Schwere, Konfidenz, Abhilfe und Regression an. Halte bestätigte Fehler, plausible Kandidaten und offene Fachentscheidungen auseinander. Bei bestehenden Ausnahmen erfasse Regel, Pfad, Begründung und Geltungsbereich. Statische Hinweise ersetzen keine Parser- oder Laufzeitbelege.

## Ergänzende Vertragsprüfung

Prüfe relevante Fixtures sowie Regeln für Ablauffristen, wiederkehrende Termine, Geschäfts- und Berichtstage. Lies vorhandene Hinweise zu Zeitzonen und Zeittypen, bevor du einen Befund hochstufst. Prüfe bei explizit geplanter Kalenderarithmetik die Absicht am Aufrufer. Eine dokumentierte Ausnahme nennt Feld, Regel, Pfad, zulässige Annahme und passenden Grenzfall. Lege zum Schluss eine kurze Inventartabelle der Zeitfelder und verbleibenden Testlücken vor.
