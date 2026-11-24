"""Compare two .NET TRX runs from the same migration slice."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from xml.etree import ElementTree


def load_trx(path):
    with path.open("rb") as stream:
        data = stream.read(32 * 1024 * 1024 + 1)
    if len(data) > 32 * 1024 * 1024:
        raise ValueError("TRX exceeds 32 MiB")
    content = data.decode("utf-8-sig")
    if "<!DOCTYPE" in content:
        raise ValueError("TRX must not contain a document type")
    root = ElementTree.fromstring(content)
    namespace, _, tag = root.tag.rpartition("}")
    if tag != "TestRun":
        raise ValueError("Expected a TRX TestRun")
    prefix = namespace + "}" if namespace else ""
    definitions = {}
    for unit in root.findall(f"{prefix}TestDefinitions/{prefix}UnitTest"):
        method = unit.find(f"{prefix}TestMethod")
        if method is None or not method.get("className"):
            raise ValueError("UnitTest without class name")
        identifier = unit.attrib["id"]
        if identifier in definitions:
            raise ValueError("Duplicate test definition ID")
        definitions[identifier] = method.attrib["className"]

    results = {}
    for result in root.findall(f"{prefix}Results/{prefix}UnitTestResult"):
        identifier = definitions[result.attrib["testId"]] + "::" + result.attrib["testName"]
        if identifier in results:
            raise ValueError(f"Duplicate TRX case: {identifier}")
        results[identifier] = result.attrib["outcome"]
    counters = root.find(f"{prefix}ResultSummary/{prefix}Counters")
    if not results or counters is None or int(counters.attrib["total"]) != len(results):
        raise ValueError("Empty, incomplete or unsupported TRX result layout")
    return results


def compare(baseline, candidate, renames):
    if not isinstance(renames, dict) or any(
        old not in baseline or not isinstance(new, str) or new not in candidate
        for old, new in renames.items()
    ):
        raise ValueError("Rename mapping does not match TRX cases")
    expected = {renames.get(name, name): outcome for name, outcome in baseline.items()}
    if len(expected) != len(baseline):
        raise ValueError("Rename mapping has overlapping targets")
    missing = sorted(expected.keys() - candidate.keys())
    added = sorted(candidate.keys() - expected.keys())
    changed = {
        name: {"baseline": expected[name], "candidate": candidate[name]}
        for name in sorted(expected.keys() & candidate.keys()) if expected[name] != candidate[name]
    }
    return {
        "parity": not (missing or added or changed),
        "baseline_outcomes": dict(Counter(baseline.values())),
        "candidate_outcomes": dict(Counter(candidate.values())),
        "missing": missing, "added": added, "changed": changed,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--renames", type=Path)
    args = parser.parse_args()
    try:
        if args.baseline.samefile(args.candidate):
            raise ValueError("Baseline and candidate must be distinct files")
        renames = json.loads(args.renames.read_text(encoding="utf-8")) if args.renames else {}
        report = compare(load_trx(args.baseline), load_trx(args.candidate), renames)
    except (OSError, ValueError, KeyError, ElementTree.ParseError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["parity"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
