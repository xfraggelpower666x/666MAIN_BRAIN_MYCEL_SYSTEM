# Community Skills und LiveCircle

## Umfang

Verglichen wurden die drei bereitgestellten Community-Skills-Archive. Der Main-Bestand enthält 5.266 Dateien, darunter 1.129 Skill-Definitionen. Die Varianten enthalten 5.263 bzw. 5.262 Dateien und 1.128 bzw. 1.127 Skill-Definitionen. Relative Pfade und SHA-256 der Dateien gleichen die Bestände ab. Bei beiden Varianten ändern sich README und Registry, der Extension-Builder fehlt und eine Root-Skill-Datei kommt hinzu. Der Migrationsvariante fehlt zusätzlich Deep Research. Der .NET-Migrationsskill ist in allen drei Fassungen identisch.

Für die Triage wurden Pfad und Frontmatter aller 1.129 Main-Definitionen gelesen. Die überlappenden Suchgruppen fanden 282 Treffer zu Engineering, Tests und Build, 64 zu Recherche und Kontext sowie 23 zu Kontinuität und Recovery. Das sind thematische Treffer, keine unabhängigen neuen Fähigkeiten. Die fachliche Vertiefung konzentrierte sich auf die folgenden siebzehn Kandidaten. Archivcode und Installer wurden nicht ausgeführt.

## Fachliche Prüfung

| Kandidaten und Fundstellen im Main-Archiv | Befund und Umsetzung |
| --- | --- |
| `nvidia-nemo-rl-session-memory/SKILL.md` 47–73, 137–168 und `opencontext/SKILL.md` 211–245 | Checkpoint mit Entscheidungen und Rückkehrpunkt ist nützlich. Der Coding Profi hat einen eigenen Handoff. Ergänzt durch Git-Nachweis und selektive Revalidierung, ohne externe Kontextdatenbank oder neue Projektidentität. |
| `systematic-debugging/SKILL.md` 50–182 und `debugging/SKILL.md` 24–158 | Erster Fehlerpfad, unterscheidende Hypothese, Gegenprobe. Diagnose bleibt bei der vorhandenen Fachfacette. Die Rehydration übergibt konkrete betroffene Vertragspfade und behandelt sie als Prüfanlass. |
| `verification-before-completion/SKILL.md` 24–40 und `agent-evaluation/SKILL.md` 238–286 | Frische Gegenprobe und Prüfung der Wirkung gegen einen eigenständigen Sollvertrag. Verwendet den bestehenden Laufbeleg-Prüfer. Ein alter Abschluss wird gezielt entwertet, wenn sein Vertragspfad driftet. |
| `using-git-worktrees/SKILL.md` 77–142, `git-workflow/SKILL.md` 155–261 und `git-workflow-mastery/SKILL.md` 153–192 | Git-Basis und isolierter Arbeitsstand sind wertvoll. Bestehendes Workspace-Routing genügt. Der Checkpoint-Abgleich benötigt eine nachgewiesene Commit-Abstammung und revalidiert betroffene Vertragspfade. |
| `bmad-orchestrator/SKILL.md` 78–122 und `legacy-modernization-orchestrator/SKILL.md` 21–37 | Prüfpunkte pro Phase und abgegrenzte Migrationsschritte. Im Plugin über Engineering-Zyklus, aktuelle Checkpoint-Graphen und zuständige Fachfacetten abgedeckt. |
| `agentic-workflow/SKILL.md` 81–132 und `workflow-automation/SKILL.md` 134–265 | Hostabhängige Session-Befehle und Task-Runner gehören zur konkreten Umgebung. Das LiveCircle-Routing bleibt der native Einstieg. |
| `context7/SKILL.md` 24–48 und `deep-research-skills/SKILL.md` 65–104 | Versionsbezogene Quellen und selektive Wiederaufnahme. Research deckt dies bereits ab. Für entscheidende neue Versionsbefunde bleiben Primärquelle und bestätigte Revision maßgeblich. |
| `dotnet-test-migration/SKILL.md` 17–22 | Migration in lauffähigen Schritten mit echter Vorher-Nachher-Prüfung. TRX-Vergleich ist seit v0.79.0 vorhanden. |
| `state-management/SKILL.md` 22–56 und 403–451 | Trennung lokaler, globaler und Serverzustände eignet sich für Frontend-Projekte. Der Plugin-Zustand bekommt keine UI- oder Netzwerk-Dependency daraus. |

Die breite Triage umfasst allgemeine und spezialisierte Fähigkeiten. Die Laufzeitintegration dieses Durchgangs konzentriert sich auf Fortsetzung und Recovery. Vollständige fachliche Einzelreviews für stackgebundene Themen sind damit nicht belegt.

## Implementierter Zusammenhang

`LiveCircle WEITER / NEXT CHAT → vorgeprüfte Projektbindung → Checkpoint + tatsächlicher Git-Diff → Strang und seine Vorgänger → Ziel-Readback oder gezielte Gegenprobe → bestätigter nächster Schritt`

Der Prüfer ist im bestehenden Checkpoint-Skript implementiert. Er zeigt, welche Stränge weiterverwendbar sind, welche Nachweise fehlen und welche abhängigen Schritte warten. Fehler im eigenen Arbeitszustand und Defekte im beauftragten Zielprojekt werden über ihre jeweils belegte Ursache an den bestehenden Reparaturablauf geleitet. Es wurde kein Fremdcode übernommen.

## Vertiefung zur lokalen Fortsetzung

| Quelle und Abschnitt | Prüfung im Ziel |
| --- | --- |
| `agentic-development-principles/SKILL.md` 46–102, 210–246 | Zwischenstände tragen erledigte Arbeit, offene Schritte und fehlgeschlagene Ansätze. LiveCircle bindet die Fortsetzung zusätzlich an den beobachteten lokalen Arbeitszustand. |
| `writing-plans/SKILL.md` 47–90 | Dateipfade, Test und kleinschrittiger Übergang präzisieren den Vertrag. Die bestehende Pfadbindung wird um Stage, Arbeitsbaum und Konflikte als unterscheidbare Beobachtungen erweitert. |
| `test-driven-development/SKILL.md` 113–168 | Gegenprobe beobachtet Fehler und Korrektur getrennt. Die lokalen Regressionen verwenden echte Git-Commits, Stage und Merge-Konflikte. |
| `testing-strategies/SKILL.md` 188–256 | Der abstrakte Statusvergleich reicht bei Git-Semantik nicht aus. Die Regressionen prüfen den Ablauf mit echten Git-Prozessen. |
| `subagent-driven-development/SKILL.md` 38–85 | Nachgelagerte Prüfung des Arbeitsergebnisses passt zur vorhandenen Rollenübergabe. Sie braucht keinen zusätzlichen automatischen Agentenstart. |
| `skill-standardization/SKILL.md` 21–52, 132–145 | Format- und Metadatenpflege hilft bei begrenzten Skill-Änderungen. Die Fremd-Konvertierung ist für diese Änderung entbehrlich. |

Eine Änderung im lokalen Index oder Arbeitsbaum konnte vorher bei identischem Commit unsichtbar bleiben. Der neue optionale Git-Statusabgleich schließt diese Lücke am normalen Checkpoint-Einstieg und gibt einschlägige Konflikte mit dem beobachteten Pfad an Recovery weiter.
