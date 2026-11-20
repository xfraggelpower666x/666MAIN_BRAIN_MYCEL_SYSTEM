# PSYLLO MYCEL R02 · ausführbarer UI-/Guidance-Bridge

OWNER=666MAIN BRAIN MYCEL SYSTEM
STATUS=LOCAL_PYTHON_VERIFIED_REMOTE_SOURCE_READBACK_PASS_HOST_PENDING
MODE=READ_ONLY_PROJECTION

Dieser Adapter nutzt den vorhandenen und unveränderten Workbench-Renderer. Er übersetzt das sechsfach native MYCEL-Menü `UI/INTELLIGENT_UI/MENU_REGISTRY.json` in sechs `views` im schon bestehenden Workbench-JSON-Datenvertrag. Ein Guidance-State im Format `psyllo.guidance-state.1` liefert `companion`-Daten. Keine automatische Tool-, Projekt- oder Netzwerkaktion.

## Aufruf

Vom Root des Repository-Checkouts mit überprüftem Git-HEAD:

```bash
python INTEGRATIONS/PSYLLO_CODING/workbench/scripts/mycel_bridge.py \
  --menu UI/INTELLIGENT_UI/MENU_REGISTRY.json \
  --state /pfad/zum/verifizierten-mycel-state.json \
  --output /pfad/mycel-workbench.json

python INTEGRATIONS/PSYLLO_CODING/workbench/scripts/render_ui.py \
  /pfad/mycel-workbench.json /pfad/mycel-workbench.html --standalone
```

Der zweite Schritt muss in der Zielumgebung gegen die reale Workbench-Assetbasis geprüft werden. Der Bridge-CLI-Prozess selbst startet nicht den Renderer und hat keine Browser-/Host-Fähigkeiten.

## State-Evidenz

Der State muss einen verifizierten `source_head` (40 Hexzeichen), `active_scope` als gültigen Workbench-Projektschlüssel, `phase`, `evidence_class`, Listen `open_obligations`/`blockers` und `owner` plus `schema` enthalten. Der bekannte letzte Schritt und die nächste erlaubte Aktion werden nur als beleggebundener Text übernommen. State darf nicht allein aus einer HTML-Ansicht abgeleitet werden.

Optionaler MYCEL-UI-Handoff: `--ui-handoff /pfad/handoff.json`. Hier sind `schema=psyllo.ui-handoff.1`, Projekt, 40-stelliger Commit und nichtleere `lineage_id` zwingend identisch zum State. Nur die lokale View-Präferenz wird übernommen. Für die spätere Nutzung von `render_ui.py --checkpoint` gilt dessen separates bestehendes Schema `scevi.visual.handoff.1`; die beiden Dateien sind nicht austauschbar.

## Abnahme

```bash
python -m unittest discover -s INTEGRATIONS/PSYLLO_CODING/workbench/tests -p 'test_mycel_bridge.py'
```

10 Fälle: 6-View-Projektion, passende View-Wiederherstellung, geänderte Revision, abweichende/fehlende Lineage, fremder Eigner, fehlerhafte SHA, unerlaubte Menüaktion, unzulässige Projektkennung und fehlende Blocker-/Action-Daten. Lokale Ausführung 10/10 bestanden auf byteidentischer Source-Kopie; CLI-Smoke-Test bestanden. Host-Klickpfade, kompletter Renderer-HTML-Lauf in der Zielumgebung, native Plugin-Parität und Fresh-Chat-Abnahme bleiben offen. Weder UI noch Shared Daemon erlangen Entscheidungs- oder Write-Autorität.

## Referenzen

- [Workbench-Skill](SKILL.md)
- [Workbench-Datenvertrag](references/ui-contract.md)
- [Native UI](../../../UI/INTELLIGENT_UI/UI_CONTRACT.md)
- [Guidance Core](../../../DAEMON/GUIDANCE_CONTRACT.md)
- [DEV Facet](../../../INTELLIGENCE/DEV/FACET_CONTRACT.md)
