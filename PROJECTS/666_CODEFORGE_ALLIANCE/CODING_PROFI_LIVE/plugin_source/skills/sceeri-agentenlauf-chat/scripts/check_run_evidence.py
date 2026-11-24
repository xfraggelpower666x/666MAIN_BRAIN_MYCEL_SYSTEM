"""Prüft lokale Laufbelege gegen einen getrennt festgelegten Abnahmevertrag."""
import argparse
from graphlib import TopologicalSorter
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Doppeltes JSON-Feld: {key}")
        result[key] = value
    return result


def read_json(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=unique_fields)


def required_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Text fehlt: {field}")
    return value


def by_id(records):
    if not isinstance(records, list):
        raise ValueError("Schritte müssen als Liste vorliegen")
    indexed = {}
    for record in records:
        identifier = required_text(record["id"], "id")
        if identifier in indexed:
            raise ValueError(f"Doppelter Schritt: {identifier}")
        indexed[identifier] = record
    return indexed


def output_path(root, name):
    if not isinstance(name, str) or not name or any(symbol in name for symbol in ("\\", ":")):
        raise ValueError("Ungültiger Artefaktpfad")
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError("Ungültiger Artefaktpfad")
    path = root.joinpath(*relative.parts).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Artefakt liegt außerhalb des Prüfverzeichnisses")
    return path


def check_step(expected, observed, root):
    if observed is None:
        return "OFFEN", "Laufbeleg fehlt"
    state = observed["state"]
    if state in ("interrupted", "timeout", "blocked"):
        return "OFFEN", state
    if state != "completed":
        raise ValueError("Unbekannter Laufzustand")
    actual_exit = observed["exit_code"]
    if type(actual_exit) is not int:
        raise ValueError("Beobachteter Exitcode muss eine Ganzzahl sein")
    if actual_exit != expected["exit_code"]:
        return "FEHLGESCHLAGEN", "Exitcode weicht ab"
    for name, digest in expected["artifacts"].items():
        path = output_path(root, name)
        if not path.is_file():
            return "OFFEN", f"Artefakt fehlt: {name}"
        with path.open("rb") as stream:
            actual = sha256()
            for block in iter(lambda: stream.read(65536), b""):
                actual.update(block)
        if actual.hexdigest() != digest:
            return "FEHLGESCHLAGEN", f"SHA-256 weicht ab: {name}"
    return "BESTANDEN", "Exitcode und deklarierte Artefakte stimmen überein"


def evaluate(contract, receipt, root):
    for document in (contract, receipt):
        if type(document["schema"]) is not int or document["schema"] != 1:
            raise ValueError("Unbekannte Schemaversion")
    for field in ("project", "revision", "run_id"):
        if required_text(contract[field], field) != required_text(receipt[field], field):
            raise ValueError(f"Beleg passt nicht zum Vertrag: {field}")

    expected = by_id(contract["steps"])
    observed = by_id(receipt["steps"])
    if not expected or observed.keys() - expected.keys():
        raise ValueError("Leerer Vertrag oder fremde Schritte im Beleg")
    graph = TopologicalSorter()
    for identifier, step in expected.items():
        dependencies = step["requires"]
        if not isinstance(dependencies, list) or any(item not in expected for item in dependencies):
            raise ValueError(f"Ungültige Vorgänger: {identifier}")
        if type(step["exit_code"]) is not int or not isinstance(step["artifacts"], dict):
            raise ValueError(f"Ungültige Erwartung: {identifier}")
        for name, digest in step["artifacts"].items():
            output_path(root, name)
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError(f"Ungültiger Soll-Hash: {identifier}")
        graph.add(identifier, *dependencies)

    results = {}
    for identifier in graph.static_order():
        step = expected[identifier]
        unmet = [dep for dep in step["requires"] if results[dep]["status"] != "BESTANDEN"]
        if unmet:
            status, detail = "BLOCKIERT", "Vorgänger ohne Abnahme: " + ", ".join(unmet)
        else:
            status, detail = check_step(step, observed.get(identifier), root)
        results[identifier] = {"status": status, "detail": detail}
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("artifacts", type=Path)
    args = parser.parse_args()
    try:
        root = args.artifacts.resolve(strict=True)
        if not root.is_dir() or args.contract.samefile(args.receipt):
            raise ValueError("Getrennte Vertrags- und Belegdateien sowie Artefaktordner erforderlich")
        results = evaluate(read_json(args.contract), read_json(args.receipt), root)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(json.dumps({"status": "UNGÜLTIG", "detail": str(error)}, ensure_ascii=False))
        return 2
    passed = all(row["status"] == "BESTANDEN" for row in results.values())
    print(json.dumps({"passed": passed, "steps": results}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
