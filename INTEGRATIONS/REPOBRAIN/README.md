# RepoBrain → 666MAIN BRAIN / CodeForge · R01

Diese Integration übernimmt den RepoBrain-Export als lokale Quelle für Abhängigkeitsanalysen. RepoBrain erzeugt den Graphen. Der Adapter validiert das Eingabeformat und liefert Knoten, typisierte Kanten, Diagnosezähler und den SHA-256 des Originalexports. CodeForge kann die Beziehungen als Ausgangspunkt für eine Impact-Map verwenden. MAIN BRAIN kann den Befund als Evidenz führen. Entscheidungen und Schreibrechte bleiben beim jeweiligen Zielsystem.

## Verwendung

Voraussetzung ist ein vorhandener RepoBrain-v2-Graph, etwa `.repobrain/knowledge_graph.json`, sowie Python 3.10 oder neuer. Übergib den tatsächlichen Commit des gescannten Checkouts.

```sh
python3 repobrain_bridge.py .repobrain/knowledge_graph.json \
  --repository OWNER/REPO --revision COMMIT_SHA > repobrain-evidence.json
```

Der Adapter nutzt die Python-Standardbibliothek, schreibt sein Ergebnis auf stdout und ruft weder RepoBrain noch einen Provider auf. Verarbeite den Export lokal. IDs können interne Datei- und Symbolnamen enthalten. Bewahre den Originalgraphen für den Readback anhand seiner SHA-256 auf.

## Vertragsgrenzen

- Repository und Commit sind vom Aufrufer deklarierte Metadaten. Der Hash belegt die eingelesenen Bytes. Für eine belastbare Bindung muss der Consumer die Herkunft des Exports separat prüfen.
- Parserfehler, generische Fallbacks oder ausgelassene Kanten mit fehlenden Endpunkten ergeben `PARTIAL`. Selbst ohne diese Hinweise ist die Gesamtdeckung `UNVERIFIED`. Der Graph kann etwa durch Scanlimits unvollständig sein.
- Die Originaltypen `imports`, `defines`, `tests` und weitere bleiben erhalten. Eine statische Importkante belegt keinen ausgeführten Aufruf. API-, Event- und Bridge-Beziehungen benötigen eigene Belege.
- GitHub-Referenz für die MAIN-BRAIN-Anbindung ist HEAD `074b281bd7950752397880b9912f620258828556` auf `666MAIN_BRAIN`. Das Paket enthält den Adapter und ein synthetisches Beispiel. Der UCA-Zielcheckout und ein produktiver Host waren hier nicht verfügbar.
