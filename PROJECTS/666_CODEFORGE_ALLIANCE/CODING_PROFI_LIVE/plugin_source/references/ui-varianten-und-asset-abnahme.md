# UI-Varianten und Asset-Abnahme

Nutze dieses Profil für beauftragte Änderungen an Dashboard, Navigation, Ansichtsvarianten und Original-Assets. Beginne am vorhandenen Renderer und seinen Projektkonventionen.

## Visuelle Invarianten pro Projekt

1. Lege gemeinsam mit der fachlichen Abnahme fest, welche Eigenschaften fest, gezielt variierbar oder noch ungeklärt sind. Typische Invarianten sind Produktname, kanonische Asset-Zuordnung, semantische Farben, Bedienelement-Bedeutung, Statuslabels und Rückkehrpfad. Layoutdichte, Akzente und Kartenreihenfolge können je Viewport oder Modus variieren, soweit der Auftrag es zulässt.
2. Vergleiche mehrere bestätigte Ansichten für wiederkehrende Regeln. Ein einzelner Screenshot begründet zunächst einen beobachteten Zustand. Bei widersprüchlichen Referenzen prüfe, ob Revision, Theme oder Viewport den Unterschied erklärt, bevor du einen Drift meldest.
3. Verwende für visuelle Regression dieselben Daten, Viewports, Theme, Schrift, Sprache und Interaktionszustände wie bei der Baseline. Prüfe zusätzlich gezielt Desktop und kleine Ansicht sowie Tastatur, Fokus, Kontrast, Überdeckung und Ausweichdarstellung. Prüfe semantische Invarianten über Labels und Rollen auch dann, wenn Pixel absichtlich abweichen.
4. Repariere die betroffene Zuordnung, Komponente oder CSS-Regel und prüfe dieselbe Ansicht erneut. Funktionskritische Abweichungen wie vertauschte Statusfarben, überdeckte Bedienelemente und falsche Aktionen erhalten die höhere Priorität.

## Asset-Provenienz und Ladeweg

- Erstelle bei einem relevanten Asset-Wechsel eine Zuordnung aus Zielprojekt, Rolle, Quelle, Dateipfad, Revision und, bei geforderter Bytegleichheit, Größe und SHA-256. Freigegebene Originale getrennt von abgeleiteten Web-Dateien führen. Prüfe Transparenz und tatsächlich gerenderte Darstellung, wenn beides gefordert ist.
- Prüfe bei einer beauftragten Weboptimierung lokale Pfade, Alternativtext, intrinsische Abmessungen, Format, Alpha und die Auswirkung auf den sichtbaren Bereich. Große eingebettete Bilddaten sind ein Anlass für einen Größen- und Ladevergleich. Lade sekundäre Ansichten bei Bedarf und prüfe den Fehlerfall. Bestehende Player-, Iframe-, Event- und Callback-Routen bleiben Teil der Regression.
- Prüfe tatsächliche Asset-Erreichbarkeit im vorgesehenen Host. Hash, lokaler Render, HTTP-Readback und Live-Deployment sind eigene Belege. Bei fehlender Bildquelle verwende die vorhandene Text- oder Branding-Ausweichdarstellung und lasse die Originalanzeige offen.

Gegenproben: ein absichtlich variiertes Layout mit gleichen Statusrollen, eine falsche Asset-Zuordnung, ein nicht ladendes Original, ein verstecktes Bedienelement auf schmalem Viewport und ein funktionierender lokaler Build mit ausstehendem Live-Readback.
