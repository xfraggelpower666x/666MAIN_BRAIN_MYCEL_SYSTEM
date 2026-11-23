# Architekturaudit v0.74.0

Basis v0.73.1. Das vollständige Paket wurde aus einem Release zurückgelesen. Gegenstand ist die Wirkungskette von Auftragsdeutung, Fachrouting und Analyse bis zu Entscheidung, Abnahme und Handoff.

| Befund | Reparatur im Kandidaten |
| --- | --- |
| A74-01 · Hoch. Review-Facette und Control Center nannten Änderungen als Default-Profil. Routing und Engineering-Zyklus verlangten für reinen Audit lesendes Vorgehen. | Moduswahl an den expliziten Auftrag gebunden. Die unabhängigen Schreibgrenzen jedes Teilziels sind in der Auftragsübergabe sichtbar. |
| A74-02 · Hoch. NLP versteht Absicht und der Zyklus kennt Repair, doch zwischen beiden fehlt ein gemeinsamer fachlicher Übergang. Improve und Repair teilen sich eine Ansicht, obwohl der erste einen Gewinn bei erhaltenen Invarianten und der zweite einen Defekt adressiert. | Gemeinsame Entscheidungshierarchie im bestehenden Routing. Sechs Arbeitsarten und getrennte Gegenproben führen über dieselbe Fachfacette und denselben Zyklus. |
| A74-03 · Mittel. Wissensfacetten empfehlen Hypothesen und Evidenz. Die Übergabe zu Codeänderung und LiveCircle band Ziel, Befund und Gegenprobe nicht durchgehend an dieselbe Arbeitsart. | Konkrete Referenzen zwischen Quelle, Aufrufer, Mechanismus, Aussagegrenze und Gegenprobe. Nach Gegenbelegen gilt eine gezielte Neuprüfung der abhängigen Schritte. |
| A74-04 · Mittel. Einzelne Fachanweisungen verlangten Windows-Starter auch außerhalb des betreffenden Zielprojekts. Das Review rundete zudem Quoten abweichend vom bestehenden SCEVI-Vertrag. | Zielprojektspezifische Abnahme und eine einzige Regel für Audit-Quoten. |

Die lokale Gegenprobe belegt die Auswertung explizit eingestufter Fakten. Der Chat-Nachweis erfolgt getrennt am jeweiligen Einstieg.
