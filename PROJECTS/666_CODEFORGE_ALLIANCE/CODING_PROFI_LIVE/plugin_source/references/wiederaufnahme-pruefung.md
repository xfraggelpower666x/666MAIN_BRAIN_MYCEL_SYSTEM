# Wiederaufnahme mit geprüfter Projektbindung

Verwende diesen Ablauf bei einem ausdrücklich vorgelegten Handoff oder bei einem unterbrochenen Coding-Profi-Strang mit vorhandenem Checkpoint.

1. Bestätige Zielprojekt, Projektwurzel oder Repo, Scope, exakten Ref und Commit aus der zuständigen Quelle. Trenne Quellbefund, Archivinhalt, beobachteten Host-Lauf und direkt zurückgelesene Zielbytes. Ein Handoff mit passender ID belegt allein keinen Start und keinen erfolgreichen Write.
2. Prüfe Struktur und Referenzen, fachliche Kausalität und schließlich das Verhalten am normalen Einstieg. Nutze die zum Format gehörende Strukturprüfung. Belege zulässige frühere Abschlüsse unabhängig, etwa mit Fundstelle, Originalrevision, überprüfbarem Receipt und Aussageumfang. Markiere eine bloß mitgelieferte Bestätigung als READBACK_PENDING. Geänderte Basis erfordert für betroffene Stränge einen Delta-Abgleich und neue Nachweise oder eine belegte Übertragbarkeit. Ein gültiger neuerer Zustand bleibt bei einer Abweichung vom Backup maßgeblich.
3. Prüfe unmittelbare und transitive Vorgänger. Abschlussverweise brauchen einen überprüften eigenen Beleg und bestätigte Vorgänger. Unbekannte, doppelte oder zyklische Referenzen sperren den betroffenen Teil des Graphen. Unabhängige Kandidaten bleiben sichtbar.
4. Behandle einen unklaren Write zuerst als Ziel-Readback. Lies Body, Revision und zuständige Sperre über den nativen Weg. Nur ein eindeutig unveränderter Zielzustand und ein tatsächlich wirksamer Versionsschutz erlauben innerhalb der Berechtigung einen Retry. Ein passender Postzustand wird als bestätigter früherer Effekt gebunden. Widersprüche bleiben offen oder im Konfliktstatus.
5. Übergib LiveCircle und der SCEVI-Daemon-Karte nur belegte Strang-ID, Basis, Befund, Abhängigkeit, Rückkehranker und nächste Aktion. Die Fachfacette prüft danach tatsächliche Autorisierung, Zuständigkeit, Schreibziele und Host und führt den nächsten zulässigen Schritt aus.

## Lesendes Python-Hilfsmittel

Der [Checkpoint-Prüfer](../skills/sceeri-coding-profi-livecircle/scripts/checkpoint_review.py) prüft die Abhängigkeitsstruktur eines tatsächlichen CodeForge-UCA-v1-Checkpoints. Aufruf ab Python 3.9:

```text
python checkpoint_review.py checkpoint.json binding.json --confirmed-complete strand-a
```

`binding.json` enthält `project`, `lineage_id`, `base_commit` (40-stelliger Git-Commit) und `scope` aus der unabhängig geprüften Projektbasis. Bei anderer Basis zuerst fachlich abgleichen. `--confirmed-complete` darf je unabhängig bestätigtem Vorgänger wiederholt werden. Der Prüfer liefert strukturelle Kandidaten, blockierende Referenzen und nicht bestätigte Abschlüsse. Er lädt keine Repositories, bestätigt selbst keine Evidenz und ersetzt weder vollständige Schema-Prüfung noch die Prüfung auf unklare Writes, Scope und Berechtigungen. Projektbindung und Bestätigungen dürfen nicht einfach aus dem vorgelegten Handoff kopiert werden.

Ein Text-Handoff bleibt über den bestehenden manuellen LiveCircle-Ablauf nutzbar. Beispiel-Checkpoints gehören in isolierte Tests.

## Host-Probe LC-01

Nutze ein vorhandenes autorisiertes Testprojekt mit einem unklaren Write und einem unabhängigen Strang. Erfasse den aktiven Rückkehranker vor der Unterbrechung. Lies bei der Wiederaufnahme zuerst das Ziel des unklaren Writes, halte den betroffenen Strang bis zur Einordnung zurück und dokumentiere, welcher unabhängige Schritt wirklich ausgeführt wird. Prüfe in der frischen Sitzung, dass der Rückkehranker zur gleichen Projektlinie gehört. Ein Exitcode des Strukturhelfers ist nur der lokale Teil dieses Nachweises.
