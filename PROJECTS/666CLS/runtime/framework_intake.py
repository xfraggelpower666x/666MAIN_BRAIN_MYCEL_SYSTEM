"""Leitet aus einem Aufnahmedossier eine prüfbare Strukturentscheidung ab."""
from cls_livecircle import require

FACTS = {
    "native_authority": "Eigene fachliche Zuständigkeit",
    "native_entry": "Eigener Start- oder Fortsetzungseinstieg",
    "own_state": "Eigener Zustand oder eigene Releases",
    "host_dependency": "Für die Kernfunktion auf das Zielsystem angewiesen",
    "same_purpose": "Gleicher fachlicher Zweck",
    "same_scope": "Gleiche Zuständigkeit",
    "compatible_lifecycle": "Kompatibler Betrieb und Release-Zyklus",
    "compatible_state": "Geprüfte Zustands- und Datenverträglichkeit",
    "continuity_preserved": "Identität, Trigger, Historie und Rückkehrpfad bleiben erhalten",
    "shared_component": "Konkret gemeinsam nutzbarer Baustein",
    "inverse_contract": "Entgegengesetzte Ein- und Ausgaberichtung",
    "package_only": "Paket enthält ausschließlich Daten, Ergebnis oder Beleg",
    "native_child": "Expliziter Child-Vertrag mit eigener Identität",
    "native_addon": "Expliziter Add-on-Vertrag ohne neuen Top-Level-Einstieg",
}
PACKAGE_FACTS = {"package_only", "native_child", "native_addon"}
TARGET_FACTS = set(FACTS) - {"native_authority", "native_entry", "own_state"} - PACKAGE_FACTS
OWNERSHIP = ("native_authority", "native_entry", "own_state")
CONSOLIDATION = ("same_purpose", "same_scope", "compatible_lifecycle",
                 "compatible_state", "continuity_preserved")


def analyze(dossier, registry):
    require(isinstance(dossier, dict), "Ein JSON-Objekt als Systemdossier angeben")
    name = dossier.get("name")
    revision = dossier.get("revision")
    require(all(isinstance(value, str) and value.strip() for value in (name, revision)),
            "Name und Revision des eingefügten Systems fehlen")
    target_id = dossier.get("target")
    require(target_id is None or isinstance(target_id, str), "Vergleichsziel ungültig")
    target = registry.get(target_id)
    target_revision = dossier.get("target_revision")
    supplied = dossier.get("facts", {})
    require(isinstance(supplied, dict) and set(supplied) <= set(FACTS), "Unbekannte Angaben im Dossier")
    used, gaps = {}, []
    for key, fact in supplied.items():
        require(isinstance(fact, dict) and type(fact.get("value")) is bool,
                f"{FACTS[key]} braucht true oder false als Wert")
        source = fact.get("source")
        if not isinstance(source, str) or not source.strip() or fact.get("revision") != revision:
            gaps.append(f"{FACTS[key]}: Fundstelle oder passende Quellrevision fehlt")
        elif key in TARGET_FACTS and (
            not target or target_revision != target["revision"] or fact.get("target_revision") != target_revision
        ):
            gaps.append(f"{FACTS[key]}: Gegenbeleg zur registrierten Zielrevision fehlt")
        else:
            used[key] = fact

    def known(key, value=True):
        return key in used and used[key]["value"] is value

    parent = dossier.get("parent")
    require(parent is None or isinstance(parent, str) and parent.strip(), "Übergeordnete Systemkennung ungültig")
    if (known("native_child") or known("native_addon")) and not parent:
        gaps.append("Child oder Add-on: native Zielkennung fehlt")
    roles = [key for key in PACKAGE_FACTS if known(key)]
    independent = known("native_authority") and (known("native_entry") or known("own_state"))
    extension = (known("host_dependency") and known("native_authority", False)
                 and known("native_entry", False) and known("own_state", False))
    same_scope = known("same_purpose") and known("same_scope")
    can_consolidate = same_scope and all(known(key) for key in CONSOLIDATION)
    if target_id and (not target or target_revision != target["revision"]):
        gaps.append("Vergleichsziel fehlt in der Registry oder seine Revision ist abgewichen")

    if (len(roles) > 1 or (known("package_only") or known("native_addon")) and independent
        or known("inverse_contract") and can_consolidate):
        decision, reason = "KONFLIKT_PRÜFEN", "Paketrolle oder Transformationsrichtung widerspricht der angegebenen Zuständigkeit oder Konsolidierung."
    elif known("package_only"):
        decision, reason = "QUELLARTEFAKT", "Der belegte Paketinhalt ist Datenstand, Ergebnis oder Nachweis."
    elif parent and known("native_child"):
        decision, reason = "NATIVES_CHILD_ERHALTEN", f"Die eigene Systemidentität bleibt im belegten Parent-Kontext {parent} erhalten."
    elif parent and known("native_addon"):
        decision, reason = "NATIVES_ADDON_ZUORDNEN", f"Der Add-on-Vertrag ordnet den Baustein {parent} zu."
    elif roles:
        decision, reason = "OFFEN", "Für die Zuordnung fehlt die native Parent- oder Zielkennung."
    elif known("inverse_contract"):
        decision, reason = "GETRENNTE_TRANSFORMATIONSWEGE", "Die belegte Ein- und Ausgaberichtung ist entgegengesetzt. Eine gemeinsame Schnittstelle ist gesondert prüfbar."
    elif independent and known("host_dependency"):
        decision, reason = "KONFLIKT_PRÜFEN", "Eigene Zuständigkeit und Abhängigkeit der Kernfunktion sind belegt. Prüfe, ob die Abhängigkeit ein Dienst oder Teil der Systemidentität ist."
    elif independent and known("shared_component"):
        decision, reason = "EIGENSTÄNDIG_MIT_GEMEINSAMEM_BAUSTEIN", "Zuständigkeit und Einstieg oder Zustand sind eigenständig. Der belegte Baustein kann gemeinsam genutzt werden."
    elif independent:
        decision, reason = "EIGENSTÄNDIGES_FRAMEWORK", "Eigene Zuständigkeit und eigener Einstieg oder Zustand tragen eine eigenständige Systemgrenze."
    elif extension:
        decision, reason = "MODUL_VORSCHLAGEN", "Das System ist auf das registrierte Ziel angewiesen und hat keine eigene Zuständigkeit, keinen eigenen Einstieg und keinen eigenen Zustand."
    elif can_consolidate and known("native_authority", False) and known("native_entry", False) and known("own_state", False):
        decision, reason = "KONSOLIDIERUNG_VORSCHLAGEN", "Zweck, Zuständigkeit, Betrieb und Daten sind kompatibel. Die Kontinuität ist im Dossier belegt."
    else:
        decision, reason = "OFFEN", "Die Befunde reichen noch nicht für eine belastbare Zuordnung."
        needed = (*OWNERSHIP, *CONSOLIDATION) if target_id else OWNERSHIP
        gaps.extend(f"{FACTS[key]}: Befund fehlt" for key in needed if key not in used)
        if same_scope:
            gaps.extend(f"{FACTS[key]}: derzeit nicht erfüllt" for key in CONSOLIDATION[2:] if known(key, False))
    return {
        "name": name, "revision": revision, "target": target_id, "target_revision": target_revision, "parent": parent,
        "decision": decision, "reason": reason, "status": "OFFEN" if decision in ("OFFEN", "KONFLIKT_PRÜFEN") else "VORGESCHLAGEN",
        "evidence": [{"label": FACTS[key], "value": fact["value"], "source": fact["source"]}
                     for key, fact in used.items()],
        "gaps": gaps,
    }
