"""R04 local source-assertion graph. Never verifies causal truth or changes authority."""
from __future__ import annotations
from collections import defaultdict
from typing import Any

POSITIVE = frozenset({"CLAIM"})
NEGATIVE = frozenset({"DENY", "COUNTEREXAMPLE"})
ALL = frozenset({"CLAIM", "DENY", "COUNTEREXAMPLE", "HYPOTHESIS", "OBSERVE", "UNKNOWN"})

def build_graph(analysis: dict[str, Any], *, max_nodes: int = 256, max_edges: int = 1024) -> dict[str, Any]:
    if not isinstance(analysis,dict) or not isinstance(analysis.get("relationships"),list):
        raise ValueError("analysis must contain relationships")
    rs = analysis["relationships"]
    if len(rs)>max_edges: raise ValueError("too many source relationships")
    node_set=set(); edges=[]; adjacency=defaultdict(set)
    for record in rs:
        a=record["source"]; b=record["target"]
        if not isinstance(a,str) or not isinstance(b,str): raise ValueError("invalid nodes")
        node_set.update((a,b))
        entries=record.get("evidence",[])
        assertions={e["assertion"] for e in entries}
        if not assertions.issubset(ALL): raise ValueError("unsupported assertion")
        supporting=[e for e in entries if e["assertion"] in POSITIVE]
        opposing=[e for e in entries if e["assertion"] in NEGATIVE]
        tentative=[e for e in entries if e["assertion"] in {"HYPOTHESIS","OBSERVE","UNKNOWN"}]
        if supporting and opposing: label="CONTRADICTED"
        elif supporting: label="SOURCE_CLAIM_UNVERIFIED"
        elif opposing: label="SOURCE_NEGATIVE_ONLY"
        elif tentative: label="UNCONFIRMED_ONLY"
        else: label="UNKNOWN"
        evidence={"support_count":len(supporting),"counter_count":len(opposing),"uncertain_count":len(tentative),
                  "support_lines":[e["line"] for e in supporting],"counter_lines":[e["line"] for e in opposing],
                  "uncertain_lines":[e["line"] for e in tentative],"truth_score":None,
                  "source_assertion_balance": len(supporting)-len(opposing),
                  "balance_not_probability": True}
        edges.append({"source":a,"target":b,"assessment":label,"evidence":evidence,
                      "independently_verified":False,"is_inferred":False})
        # Only explicit source CLAIM edges may be traversed, without believing the claim.
        if supporting: adjacency[a].add(b)
    if len(node_set)>max_nodes: raise ValueError("too many graph nodes")
    nodes=sorted(node_set)
    # Derive reachability of *assertion paths*, not additional asserted causal edges.
    paths=[]; cycle_paths=[]
    for start in nodes:
        stack=[(start,[start])]
        while stack:
            current,path=stack.pop()
            if len(path)>min(max_nodes, len(nodes)+1): continue
            for nxt in sorted(adjacency[current], reverse=True):
                if nxt==start:
                    cyc=path+[nxt]
                    if len(cyc)>2: cycle_paths.append(cyc)
                elif nxt not in path:
                    npath=path+[nxt]
                    if len(npath)>=3: paths.append({"nodes":npath,"status":"ASSERTION_CHAIN_ONLY_NOT_CAUSAL_PROOF","inferred_edge_created":False})
                    stack.append((nxt,npath))
                # Stop boundedly without implying transitive causation.
                if len(paths)>max_edges*max_nodes:raise ValueError("too many paths")
    return {"schema":"666CURES_R04_GRAPH_V1","nodes":nodes,"edges":edges,
            "assertion_paths":paths,"cycles":cycle_paths,
            "source_field_conflicts":analysis.get("field_conflicts",[]),
            "independently_verified":False,"transitive_causation_inferred":False,
            "new_causal_edges_inferred":[],"authority_changed":False,"mutations":[],
            "evaluation_policy":"COUNTS_ARE_SOURCE_ASSERTION_COUNTS_NOT_TRUTH_PROBABILITIES"}
