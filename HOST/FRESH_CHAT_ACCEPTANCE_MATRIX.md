# FRESH CHAT ACCEPTANCE MATRIX

PLUGIN_ID=plugins_6aeecd97365081918f3813165617c17c
RELEASE_ID=pluginrel_6aeecd98b5fc81918211f89ff71ccd0e

| Case | Expected trigger | Write authority | Current status |
|---|---|---|---|
| SYSTEMSTART | 666MAIN BRAIN SYSTEMSTART | NONE | PENDING_FRESH_CHAT_ACCEPTANCE |
| STATUS | 666MAIN BRAIN STATUS | NONE | PENDING_FRESH_CHAT_ACCEPTANCE |
| HELP | 666MAIN BRAIN HELP | NONE | PENDING_FRESH_CHAT_ACCEPTANCE |
| WEITER | 666MAIN BRAIN WEITER | bounded continuity | PENDING_FRESH_CHAT_ACCEPTANCE |
| NEW CHAT | 666MAIN BRAIN NEW CHAT | governed continuity persistence only | PENDING_FRESH_CHAT_ACCEPTANCE |
| NEXT CHAT | 666MAIN BRAIN NEXT CHAT | NONE unless governed continuity write requested | PENDING_FRESH_CHAT_ACCEPTANCE |
| VORNE | 666MAIN BRAIN VORNE | NONE | PENDING_FRESH_CHAT_ACCEPTANCE |
| DASHBOARD | 666MAIN BRAIN DASHBOARD | NONE | PENDING_FRESH_CHAT_ACCEPTANCE |
| FUCK HORST | FUCK HORST | NONE | PENDING_FRESH_CHAT_ACCEPTANCE |
| UPDATE | 666MAIN BRAIN UPDATE | governed repo writes | PENDING_FRESH_CHAT_ACCEPTANCE |

SOURCE_PASS=TRUE
DELIVERY_PASS=TRUE
INSTALLATION_PASS=TRUE
SKILL_ROUTER_ADOPTION_PASS=TRUE
SKILL_DISCOVERY_PASS=TRUE
SKILL_DIRECT_READ_PASS=TRUE
HOST_PASS=FALSE
HOST_PASS_MAY_NOT_BE_INFERRED=TRUE

## Current host observation — 2026-11-14

PLUGIN_INSTALLATION=VERIFIED
SKILL_LIST_DISCOVERY=8_OF_8_LISTED_2026_11_14
DIRECT_SKILL_READ=8_OF_8_PASS_2026_11_14
ADOPTION_CLASS=VERIFIED_SKILL_ROUTER_ADOPTION
FRESH_CHAT_TEST=NOT_YET_FULLY_EXECUTED
OBSERVATION_SCOPE=2026_11_14_CURRENT_CHAT_ONLY
TEN_TRIGGER_HOST_PASS=FALSE

## Release 0.2.0 · R12

Beobachteter privater MAIN-BRAIN-Release: `0.2.0` / `pluginrel_6af807d884d48191bd24fbec19d46e4e`. Der vorhandene Repository-Quellsnapshot und die frühere Host-Beobachtung beziehen sich auf 0.1.0. Für 0.2.0 sind das gespeicherte Release und die lesbaren Quelldateien bestätigt. Skill-Discovery und Fresh-Chat-Ausführung für 0.2.0 sind offen.

Die zehn nativen Fälle bleiben für 0.2.0 offen. Coding-Einstieg, Audit-Ansicht und projektgebundene Wiederaufnahme sind zusätzliche Coding-Fälle. [Abgleich](../AUDIT/MAIN_BRAIN_CODING_PLUGIN_PARITY_R12_2026-11-14.md)

## Release 0.2.2 · R13

Der private Account-Release 0.2.2 / `pluginrel_6af80d93c58c8191a833888a3a53ff49` ist gespeichert und direkt zurückgelesen. Der Repository-Paketsnapshot bleibt die historische Quelle für 0.1.0. Die Host-Sitzung bestätigte bei 0.2.1 alle acht nativen MAIN-BRAIN-Einstiege und den Coding-Einstieg per direktem Skill-Readback. Nach Publikation von 0.2.2 war `sceeri-projektsprachen` im laufenden Chat weiterhin nicht gelistet oder direkt lesbar. Release-spezifische Fresh-Chat-Ausführung bleibt offen.

[Abgleich](../AUDIT/MAIN_BRAIN_PLUGIN_BINDING_R13_2026-11-14.md)

## Release 0.2.2 · Discovery R14

Für den privaten Account-Release 0.2.2 / `pluginrel_6af80d93c58c8191a833888a3a53ff49` sind in dieser Host-Sitzung **109/109 Skill-IDs sichtbar** und **109/109 Skill-Dateien direkt lesbar und bytegleich zur Paketquelle**. `sceeri-projektsprachen` ist darunter. Die R13-Beobachtung der fehlenden Sprachfacette ist für den jetzigen Host-Stand abgelöst. Die Ausführung der nativen und Coding-Trigger in frischen Chats sowie Provider-Verhalten sind weiterhin offen.

[Abgleich](../AUDIT/MAIN_BRAIN_SKILL_DISCOVERY_R14_2026-11-14.md)

## Coding · Peer-Tool-Intake (Freeze-ZIP)

| Teilprüfung | Status |
| --- | --- |
| Wiederverwendung des vorhandenen CodeForge-Prüfers | `PASS` im bereitgestellten Erstbericht |
| Kanonische Klasse und Vertrags-Blob | `PASS_WITH_FOLLOWUP` im selben Chat, GitHub-Readback bestätigt |
| Exakte Klasse und Vertragsbeleg im Erstaufruf mit aktualisiertem Workflow | `OPEN` |
| Zuordnung des Testlaufs zu einer konkreten Plugin-Release-ID | `OPEN` |

[Nachweis und erneute Abnahme](../AUDIT/PEER_TOOL_INTAKE_HOST_RECHECK_2026-11-14.md)

## Release 0.2.6 · Coding-Paket-Readback

Der aktuelle private Release `0.2.6` / `pluginrel_6af8c3ed5b408191b69c88d94e735fc3` wurde über die Release-Metadaten und zwei Paketdateien direkt gelesen. Repository-Basis der Gegenprobe: `8ab53c8500aae515fef5a739744b2d8bc9468aef`.

- `references/main-brain-coding-integration.md` verweist auf den App-Router und deklariert den Abgleich der Coding-Fachfacetten mit L.Y.V.R.A. CODING PROFI 0.63.1. Der Vermerk allein belegt keine vollständige Funktionsparität.
- `references/main-brain-repo-coding-workflows.md` fordert beim ersten Tool-Ergebnis die exakte Vertragsklasse, den Toolpfad, die Vertragsdatei, den gepinnten Commit und den Blob-SHA. Ohne direkten Vertrags-Readback bleibt die Klasse offen. Die Regel stimmt mit dem gebundenen Repository-Workflow überein.
- Die frühere Freeze-ZIP-Gegenprobe bleibt `PASS_WITH_FOLLOWUP` ohne belegte Release-Zuordnung. Für 0.2.6 stehen der Erstaufruf in einem frischen Chat und die Host-Ausführung des Coding-, App- und UI-Workflows aus.

Recovery: Preimage dieser Matrix `926e991e940bbdbf77142ef577fd026c60ad454f` und des Current Pointers `66fed8364a87ef10774bcc07bcbee78196db2501`, beide wiederherstellbar am genannten Basiscommit.

## Release 0.2.7 · Ausführungskontrolle im Coding-Paket

Privates Account-Release `0.2.7` / `pluginrel_6afb018c03a88191a84790ba36989e8f`. Der gespeicherte Release-Stand und die veröffentlichte Paketquelle sind verifiziert. Der vollständige Archivvergleich gegen 0.2.6 plus das freigegebene Update ergab 196 übereinstimmende Dateien und 112 Skills. Neun Update-Dateien wurden zusätzlich direkt zurückgelesen.

- `references/coding-ausfuehrungskontrolle.md` bindet die aus dem SYSTEM_BUILD_CONTROL_KERNEL v10.2 übernommenen Regeln für Auftragsentscheidung, Sicherung, Gegenprobe und begrenzte Fehlerbehebung an PSYLLOs Coding-Ablauf.
- Die Routing-Anbindung an Coding, LiveCircle, Engineering-Zyklus und Daemon ist in der Paketquelle belegt. Projektstatus, Schreibberechtigungen und kanonischer Current werden weiterhin über die bestehenden Verträge aufgelöst.
- Die praktische Ausführung in einem frischen Chat bleibt offen. Insbesondere sind lesendes Audit mit eingebettetem Trigger, begrenzte Reparatur, Ziel-Readback nach unterbrochenem Write und blockierte Freigabe bei fehlender Pflichtprüfung als Host-Fälle nachzuweisen. Hierfür liegt kein Ausführungsbeleg vor.

Recovery: unveränderter Basiscommit `a4572e65744d7d1795f95cb6e0b301ebc8434e56`, Preimage der Matrix `2f4270dae36d0fca1994f603220ef2c48f9cb722` und des Current Pointers `483e30cd5163f32cf351ecf74ce1414bccf4e8d6`. Der Paketnachweis ändert den Migrations-Gate-Status nicht.

## Release 0.2.8 · PSYLLO-Coding-Rehydration und Workbench

Privates MAIN-BRAIN-Release `0.2.8` / `pluginrel_6afdcf591fb88191aaad24a6e8cef7b3`. Direkter Paket-Readback `23/23`. Repository-Integrationscommit `9c7e6ead2ee4ac9c2a6ed47eb400d7a854a809a1`, Quell-Readback `19/19`.

- Lokale Abnahme: Git-Checkpoint `12/12`, Laufbeleg `8/8`, Workbench `10/10`. Die eingebetteten JavaScript-Blöcke bestehen die Syntaxprüfung.
- Fresh Chat: offen. Zu prüfen sind Coding WEITER und NEXT CHAT im gebundenen Projekt, ein fehlendes oder falsches Laufartefakt, die Workbench-Navigation und der UI-Handoff nach Projekt- und Revisionsbindung.
- Persistenz einer UI-Präferenz, Host-Klickpfade und Plugin-Ausführung benötigen einen eigenen Beleg.
- Rückkehrbasis: [Pre-change recovery](../AUDIT/PRECHANGE_PSYLLO_CODING_2026-11-18.md).
