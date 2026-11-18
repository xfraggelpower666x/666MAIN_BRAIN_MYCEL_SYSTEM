# 666LINGUA-Live-Abgleich für Desktop 1.1.0

## Direkt gelesene Basis

- **VERIFIZIERT.** Der Drive-Live-State-Pointer nennt 3.4.6/R18 und liegt im autorisierten Ordner `05_STATE/00_LIVE_CURRENT`. Der direkt gelesene Live-Handoff bestätigt v3.4.6/R18 und enthält die getrennte Rehydrierungsreihenfolge für Oberflächensprache, Quell- und Zielprofil, Locale und Zeitzone.
- **VERIFIZIERT.** Das MAIN-Artefakt aus dem produktiven Current-Ordner hat SHA-256 `41b6ca45ad0027b346bd05aac0c7c9544f364e093734241516a5ec3c32f04478`. Der Hash stimmt mit dem R18-Provider-Audit überein. Alle 226 internen Inventareinträge stimmen. Die Release-Version im Manifest lautet 3.4.6. Die eingebettete Pointer-Kopie enthält noch die ältere Portable-Kennung R13. Für den Live-State-Abgleich stützen sich die Desktop-Angaben auf den direkt gelesenen State und das bestätigte MAIN-Artefakt.
- **READBACK_PENDING.** Ein separater globaler Publikationspointer liegt im sichtbaren Bootstrap-/Current-Baum nicht als eigenständig lesbares Artefakt vor. Die hochgeladenen R19-ZIPs bleiben Kandidatenquellen für Desktop-Sprachbelege.
- Private Profil- und Lerndaten aus dem nativen Live-System sind keine Desktop-Testdaten. Die App speichert Registrierungen in ihrem lokalen Windows-Profil.

## Ergebnis

| Live-Vertrag | Desktop 1.1.0 |
| --- | --- |
| `docs/STARTUP_HELP_LANGUAGE_PROFILE_CONTRACT_v3.4.6.md` | Oberfläche EN/DE, English als Erststart, separate dauerhaft gespeicherte Übersetzungsrichtung. Lokale Registrierung und optionaler Partner. |
| `docs/TEMPORAL_CONTEXT_CORE_v3.4.6.md` | Zwei Locale- und Zeitzonenuhren. Dauerhafte bestätigte Zonen, lokale Ortssuche und Umrechnung aus Datum + Uhrzeit + IANA-Zonen. UTC-Offsets, Zeitdifferenz, Kalendertagwechsel und DST-Fehlerpfade. |
| `docs/USER_RELATIONSHIP_LEARNING_AND_EMOJI_CONTRACT_v3.4.6.md` | Lernfreigabe mit prüfbarem Treffer. Der manuelle Emoji-Assistent ergänzt die vorhandene semantische Emoji-Verstärkung. |
| `runtime/LINGUA_LIVE_CIRCLE_RUNTIME_CONTRACT_v3.4.6.md` und `docs/SEMANTIC_RELATIONAL_TRANSLATION_CONTRACT_v3.4.6.md` | **PARTIAL.** Der Desktop-Kern bleibt evidenz- und phrasenbasiert. Eine vollständige Freitext-Engine, automatische Kontextauflösung für relative Zeit im Satz sowie semantische Rückprüfung und sitzungsübergreifende Fortsetzung des nativen KI-Hosts sind offen. |
| Native visuelle Statusdarstellung | Der Desktop zeigt Sprachrichtung, Zeitkontext, Sprachbelege, Version und Prüfgrenzen in seinem eigenen UI. |

## Eingebettete Datensätze

- Ortsdaten nach `city-timezones` 1.3.4 (npm-Lizenzangabe MIT), reduziert auf Ort, Region, Ländercode und IANA-Zone. Winterberg wurde als zusätzlicher Eintrag aufgenommen. [city-timezones](https://github.com/kevinroberts/city-timezones)
- Emoji-Daten und Suchbegriffe nach `emojibase-data` 18.0.0, MIT. [Emojibase](https://github.com/milesj/emojibase)
- Windows-Vollbild verwendet die dokumentierten Edge-Kioskparameter. [Microsoft Learn](https://learn.microsoft.com/deployedge/microsoft-edge-configure-kiosk-mode)
