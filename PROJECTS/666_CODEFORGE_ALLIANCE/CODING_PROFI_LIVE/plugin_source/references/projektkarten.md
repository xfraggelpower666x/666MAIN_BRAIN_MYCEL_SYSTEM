# Bilinguale Projektkarten für Entwicklung und Handoff

Nutze das Profil bei einem beauftragten Projektmanifest, einer Exportdokumentation oder einer zweisprachigen Übergabe. Die Referenz [projektkarten-vorlage.json](projektkarten-vorlage.json) enthält neutrale Beispiele.

1. Setze stabile Karten-IDs und eine gemeinsame Formatversion. Bewahre Projekt-ID, Revision, Pfade, Evidenz-IDs, Entscheidungscodes und technische Werte beim Sprachwechsel. Übersetze Titel, Beschreibungen und Nutzungsanweisungen. Bei echten Ausgangskarten erhält der Import die bereits belegten IDs.
2. Trenne Projektidentität, Beiträge und Komponentenherkunft, technische Evidenz und Entscheidungen in Karten. Verknüpfe Entscheidungen über IDs mit Befund, Revision, Test und offenem Schritt. Gib bei Drittabhängigkeiten Fundstelle und belegten Lizenzstatus an. Ungeklärte Rechte bleiben offen. Private Kontakt-, Impressums- und Betriebsdaten gehören nur in den dafür beauftragten Zielkontext.
3. Nutze `null` für unbekannte Einzelwerte und eine leere Liste für einen erfassten Bestand ohne Einträge. Fehlt der Nachweis über den Bestand, dokumentiere den Umfang der Prüfung. Übernimm vorhandene Werte mit belegter Herkunft.
4. Validiere JSON, Eindeutigkeit je Karten-ID und Sprache, Sprachenparität, Verweise und Gleichheit der sprachneutralen Werte. Prüfe sensible oder noch ungeklärte Felder vor Weitergabe separat. Eine Projektkarte überträgt keine Freigabe oder Eigentumsrechte.

Gegenproben: Revision unterscheidet sich zwischen DE und EN, Evidenz-ID ist nicht auflösbar, Rechteangabe fehlt oder ein alter Nachweis passt nicht zum Kandidaten. Melde den konkreten Konflikt an der betroffenen Karte.
