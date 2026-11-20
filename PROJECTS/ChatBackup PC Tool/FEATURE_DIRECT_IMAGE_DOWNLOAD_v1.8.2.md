# Direct Chat Image Download — v1.8.2

## Ziel

Chat-Bilder sollen unabhängig vom Portable-ZIP direkt aus dem Chat-Bildbrowser gespeichert werden können.

## Bedienung

- **Download** auf einer Bildkarte: einzelnes Bild speichern.
- **Download** in der Großansicht: einzelnes Bild speichern.
- **Ausgewählte herunterladen / Download Selected**: alle angehakten, direkt erreichbaren Bilder in einen Zielordner speichern.
- **Alle erreichbaren herunterladen / Download All Reachable**: alle Bilder mit abrufbarer HTTP(S)-URL in einen Zielordner speichern.

## Datenformat

Bilddateien werden als Original-Binärbytes geschrieben. Es findet keine Base64-Kodierung statt. Portable ZIP legt erfolgreich geladene Bilder ebenfalls als Binärdateien in `assets/` ab.

## Fail-closed

Interne ChatGPT-Asset-Pointer ohne direkt erreichbare Bildbytes werden nicht erfunden oder in Base64-Platzhalter verwandelt. Sie bleiben als Metadaten mit Status erhalten.
