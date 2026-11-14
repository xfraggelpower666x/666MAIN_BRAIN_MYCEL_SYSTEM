"""Convert a local RepoBrain v2 graph to a portable evidence record."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing or invalid {field}")
    return value


def convert(raw, repository, revision):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Repository must be owner/name")
    if not re.fullmatch(r"(?:[a-f0-9]{40}|[a-f0-9]{64})", revision):
        raise ValueError("Expected a full lowercase Git commit hash")

    graph = json.loads(raw)
    if not isinstance(graph, dict) or graph.get("schema") != "repobrain-knowledge-graph-v2":
        raise ValueError("Expected repobrain-knowledge-graph-v2")
    if not all(isinstance(graph.get(key), list) for key in ("nodes", "edges")):
        raise ValueError("Graph nodes and edges must be arrays")
    diagnostics = graph.get("diagnostics")
    if not isinstance(diagnostics, dict):
        raise ValueError("Expected graph diagnostics")
    diagnostic_counts = {}
    for key in ("generic_fallback_files", "parse_error_files"):
        if not isinstance(diagnostics.get(key), list):
            raise ValueError(f"Expected diagnostics array {key}")
        diagnostic_counts[key] = len(diagnostics[key])

    ids = {}
    nodes = []
    portable_ids = set()
    for node in graph["nodes"]:
        if not isinstance(node, dict):
            raise ValueError("Graph node must be an object")
        source_id = require_text(node.get("id"), "node id")
        kind = require_text(node.get("type"), "node type")
        if source_id in ids:
            raise ValueError(f"Duplicate node id: {source_id}")
        # Portable IDs remove absolute workspace paths from the graph carrier.
        node_id = "workspace" if kind == "workspace" else source_id
        if node_id in portable_ids:
            raise ValueError(f"Duplicate portable node id: {node_id}")
        portable_ids.add(node_id)
        ids[source_id] = node_id
        nodes.append({"id": node_id, "type": kind})

    edges = []
    dangling = 0
    for edge in graph["edges"]:
        if not isinstance(edge, dict):
            raise ValueError("Graph edge must be an object")
        source = require_text(edge.get("from"), "edge source")
        target = require_text(edge.get("to"), "edge target")
        kind = require_text(edge.get("type"), "edge type")
        if source not in ids or target not in ids:
            dangling += 1
            continue
        edges.append({"from": ids[source], "to": ids[target], "type": kind})

    return {
        "schema": "repobrain-codeforge-evidence-v1",
        "provenance": {
            "producer": "RepoBrain",
            "source_schema": graph["schema"],
            "graph_sha256": hashlib.sha256(raw).hexdigest(),
            "repository": repository,
            "revision": revision,
            "repository_and_revision_status": "CALLER_DECLARED",
        },
        "classification": {
            "source": "LOCAL_GRAPH_READ",
            "authority": "EVIDENCE_ONLY",
            "coverage": "PARTIAL" if dangling or any(diagnostic_counts.values()) else "UNVERIFIED",
            "host_verified": False,
        },
        "diagnostics": {**diagnostic_counts, "dangling_edges_omitted": dangling},
        "counts": {
            "nodes": len(nodes),
            "edges": len(edges),
            "edge_types": dict(sorted(Counter(edge["type"] for edge in edges).items())),
        },
        "nodes": nodes,
        "edges": edges,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    try:
        result = convert(args.graph.read_bytes(), args.repository, args.revision)
    except (OSError, ValueError) as error:
        parser.exit(2, f"{error}\n")
    json.dump(result, sys.stdout, ensure_ascii=True, indent=2)
    print()


if __name__ == "__main__":
    main()
