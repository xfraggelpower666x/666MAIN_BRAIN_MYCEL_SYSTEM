# Recovery und Audit · Coding-, App- und UI-Workflow

Basis: Branch `666MAIN_BRAIN`, Commit `bc1d8a6a42549c96d80d3c18482d9b84511cfb01`.

| Datei | Preimage |
| --- | --- |
| `INTEGRATIONS/PLUGIN_CAPABILITIES/WORKFLOWS_R01.md` | `dddd17d59569516e6c51bb0319af441f6dbe2846` |
| `CURRENT_POINTER.md` | `df9eb155b93c86b70b72ea6c5ef6eb8c4cdd1abe` |

Die Preimages sind über den Basiscommit wiederherstellbar. Der Workflow erhält einen neuen Abschnitt vor „Modus und Evidenz“. Der vorhandene Text, die Workflow-IDs und die Current-Bindung bleiben erhalten.

| Bewerteter Beitrag | Entscheidung | Ziel |
| --- | --- | --- |
| Auftragstyp für Coding, Review und Textarbeit, Freigabegrenze beim externen Builder | `ADD_TO_EXISTING_TOOL` | Bestehender Coding-Workflow |
| App-Abnahme für Zustände, Formulare, Client-/Server-Grenze und Barrierefreiheit | `ADD_TO_EXISTING_TOOL` | Bestehende Engineering- und Abnahmeverfahren |
| Quellgebundene Wiederverwendung von UI-Komponenten mit Nachweis im Zielprojekt | `ADD_TO_EXISTING_TOOL` | Bestehender Engineering-Workflow |
| Konkreter externer Komponentenprovider | `HOLD_FOR_REVIEW` | Zugriff, Zielverträglichkeit und beobachtete Ausführung offen |

Statische Gegenprobe: 7/7 Vertragsfälle auf vorhandene Regeln geprüft. Der ursprüngliche Workflow ist durch Entfernung des neuen Abschnitts vollständig rekonstruierbar. Current Pointer und Runtime-Registry referenzieren denselben Workflow. Die bisherige Host-Abnahme für den Erstaufruf des Peer-Tool-Intake bleibt offen. Plugin-Paketierung und Ausführung dieses neuen Workflow-Deltas im Host sind separat zu belegen.
