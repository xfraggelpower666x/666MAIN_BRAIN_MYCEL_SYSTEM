# Chat Image Browser — v1.4.0

Ziel: Bilder aus dem geladenen Chat nicht nur als Asset-Metadaten behandeln, sondern galerieartig sichtbar machen und eine echte Auswahl für den Backup-Export ermöglichen.

## Verhalten

1. Nach Share-Import werden alle strukturierten Bild-Assets ermittelt.
2. Jedes Bild erhält einen stabilen `assetKey`.
3. Der Bildbrowser zeigt Karten nach Nachricht/Autor.
4. Direkt erreichbare URLs werden parallel mit maximal vier Hintergrund-Workern geladen und über Pillow als Thumbnail dargestellt.
5. Der Benutzer wählt per Checkbox, welche Bilder physisch in das Portable-ZIP sollen.
6. Auswahlzustand wird zusätzlich in JSON/JSONL und `package_manifest.json` dokumentiert.
7. Interne Pointer ohne Direkt-URL bleiben sichtbar und maschinenlesbar, werden aber nicht als vorhandene Bilddatei vorgetäuscht.

## Status

SOURCE_IMPLEMENTATION=PASS
GUI_GALLERY_SMOKE=PASS
SELECTIVE_DOWNLOAD_FIXTURE=PASS
WINDOWS_RUNTIME_READBACK=PENDING
