# Quellenabgleich v0.35.0

| Quelle | Übernahme |
| --- | --- |
| SCEVI R01, 16 Dateien, 14 SHA-256-Einträge geprüft | Exakte Farbwerte bestätigt. Interaktion, Tastatur und mobile Lesbarkeit, Zeitzonen, temporärer Zustand und Statusabnahme im [SCEVI-Vertrag](scevi-visual-contract.md). |
| artifacts(1).zip, 57 Dateien einschließlich zweier geprüfter Unterarchive | Sieben Fullstack-Skills decken vorhandene Entwicklungs- und Testfacetten ab. Vier Visual-Skills entsprechen den vorhandenen Semantik-, Kausal-, Evidenz-, Emergenz- und SCEVI-Abläufen. Ergänzt sind [Kausaltypen](../skills/sceeri-causal/SKILL.md), [NLP-Integrationsprüfung](nlp-integrationspruefung.md) und [UI-Abnahme](chat-abnahme.md). |
| chatgpt-skills-main(3).zip | Bytegleich mit der in [Herkunft](herkunft.md) erfassten Quelle. Die zwölf bestehenden Fachzuordnungen bleiben gültig. Die enthaltenen Nebenarchive für Karten, ROI und Skill-Erstellung fallen unter die vorhandenen Geodaten-, Finanz- und Facettenentwurfsabläufe. |
| GeeksforGeeks, How To Utilize ChatGPT To Improve Your Coding Skills? | Freiwilliger [Übungsmodus](../skills/sceeri-coding-uebung/SKILL.md), [Pseudocode-Übergang](../skills/sceeri-code-writer/SKILL.md) und [Technologievergleich](../skills/sceeri-research/SKILL.md). |

Python-, Java-, Web- und Testdateien dienen als Quellen für fachliche Prüfschritte. SCEVI R01 beschreibt Chat-Interaktion. Der lokale Web-Prototyp aus dem zweiten Archiv prüft seine eigene Navigation und belegt keinen Nutzerturn in ChatGPT. Externe NLP-Dienste, Registrierung und Speicherung setzen jeweils die passende autorisierte Zielprojektanbindung voraus. Die UI-Abnahme im ChatGPT-Host bleibt OFFEN.

## Detailnachprüfung in v0.36.0

Die beiden Unterarchive aus `artifacts(1).zip` enthalten zusammen 55 Dateien. Alle 55 sind bytegleich als Einzeldateien im Außenarchiv vorhanden. Damit bilden die Unterarchive zwei Projektstrukturen aus bereits enthaltenen Einzeldateien ab. Die Stichworte aus v0.35.0 deckten die Hauptabläufe ab. Konkrete Java-, NLP-, Reporting- und Reasoning-Prüffälle sind jetzt in den vorhandenen Facetten vertieft.

| Material | Umsetzung |
| --- | --- |
| Python-Analyse, FastAPI, Java-Client und HTML-Bericht samt Tests | [Quellnahe Gegenproben](nlp-integrationspruefung.md#prüffälle-aus-den-fullstack-artefakten) für Sprache, Offsets, Berichtserreichbarkeit, Auftragstrennung und Fehlertypen. |
| Evidence Engineering und Reasoning-Addon | [Entscheidung und Widerlegung](../skills/sceeri-evidence/SKILL.md#technische-entscheidung-mit-gegenbeleg) sowie [Systemwechselwirkungen und Komplexität](../skills/sceeri-emergence/SKILL.md#wechselwirkungen-und-komplexität). |
| Web-Dashboard, Datenmodell und UI-Checkliste | [Navigation und Zustandsabnahme](chat-abnahme.md#navigation-aus-dem-web-prototyp-übertragen). Die kanonische SCEVI-Palette bleibt die gültige Chat-Oberfläche. Beispielwerte für Gesundheit und Konfidenz dienen keinem Statusnachweis. |
| Projektsetup, Migration, Styleguides und Promptbeispiele | Projektspezifische Beispiele. Die bestehenden Engineering-, Review-, Python-, Java-, Web-, NLP- und Testfacetten führen die fachlichen Abläufe. Setup- und Migrationsschritte beziehen sich auf das jeweilige Zielprojekt. |

Diese Nachprüfung beruht auf Quellvergleich und Paketvalidierung. Die Beispielserver und die Host-Klickprüfung wurden dabei nicht ausgeführt.
