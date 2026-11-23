---
name: cls-visual
description: Erstellt die 666CLS-Archivansicht aus einem verifizierten LiveCircle-Stand und nimmt passende UI-Handoffs wieder auf.
---

Öffne zuerst den nativen GitHub-Current-Pointer und prüfe den referenzierten Stand. Der lokale Einstieg ist `python runtime/cls_livecircle.py "666CLS SYSTEMSTART" --dashboard ../666cls.html`. Der Renderer nutzt bestandsbezogene Daten, Diagramme und Auditinformationen aus 666CLS. Ein UI-Handoff wird über `--checkpoint` ausschließlich für dieselbe 666CLS-Identität und Revision übernommen.
