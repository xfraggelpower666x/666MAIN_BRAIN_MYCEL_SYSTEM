---
name: sceeri-sprachassistent
description: "Plant Sprachassistenten für Zielprojekte und prüft Transkription, Antwort, Sprachausgabe und Rückfallpfade."
---

# Sprachassistent entwerfen

Modelliere Aufnahme, Erkennung, sichtbares Transkript, Modellantwort und Ausgabe als getrennte Schritte. Kläre Sprache, Berechtigung, Aufnahmeende und bei Bedarf expliziten Abbruch. Ohne verfügbare Audiofunktion verwende bereitgestellten Text und gib eine lesbare Antwort aus.

Für externe Zielprojekte entscheide, welche Verarbeitung lokal oder beim Anbieter erfolgt. Lege den Umgang mit Aufnahmen und Transkripten fest. Verwende sichere Konfiguration mit Platzhaltern für Zugangsdaten. Prüfe die tatsächliche SDK-Version des Zielprojekts, bevor du eine alte API übernimmst.

Teste Stille, Umgebungsgeräusch, Nichterkennung, Netzwerkfehler, Timeout und fehlende Sprachausgabe. Kennzeichne, ob Eingabe, Transkription oder Audioausgabe tatsächlich beobachtet wurde.

## Spracheingabe im Chat

Nutze das Transkript, das der Chat tatsächlich als Nutzereingabe liefert. Sind Dateiname, Pfad, Versionsnummer oder Zielaktion in der Spracheingabe mehrdeutig, frage nur nach dem betroffenen Ausdruck. Bei fehlendem Transkript bitte um Text. Gib Befund und nächsten Schritt in lesbarer Form aus, auch wenn eine Sprachausgabe verfügbar ist. Das Plugin fordert keine Zugangsdaten an und steuert kein Mikrofon. Für Laufzeitentwürfe eines externen Sprachprojekts siehe [Chat-Betriebsmodell](../../references/chat-betriebsmodell.md#paket-und-zielprojekt).
