"""666CURES isolated new candidate R04 -- NOT the lost original engine.
Pure deterministic transformer: no filesystem/network, no external calls, no shared state.
Results use evidence trace; original source text is treated as data, not commands.
"""
from __future__ import annotations

import re
from typing import Any

MAX_SOURCE_CHARS = 32_000
ALLOWED_KINDS = frozenset({
    'KEY_VALUE','STATUS','RELATION','DEPENDENCY','ARCHITECTURE_NOTATION',
    'LIFECYCLE','PSEUDOCODE','SYMBOLIC_TECHNICAL_SHORTHAND'
})


def _render_kv(k: str, v: str, fields: dict[str, str]) -> str:
    if k == 'SYSTEM_ID': return f'Die angegebene Systemkennung lautet {v}.'
    if k == 'CHILD_AUTOLOAD' and v == 'FORBIDDEN': return 'Das Child darf nicht automatisch geladen werden.'
    if k == 'CROSS_CHILD_MERGE' and v in ('FALSE','FORBIDDEN'): return 'Eine Zusammenführung verschiedener Child-Systeme ist untersagt.'
    if k == 'STATUS' and v == 'READBACK_PENDING': return 'Der direkte Readback steht noch aus.'
    if k == 'TEST_RESULT' and v == 'UNKNOWN': return 'Das Testergebnis ist unbekannt.'
    if k == 'HISTORICAL_STATE': return f'Der historische Zustand lautet {v}; er ändert einen aktuellen HOLD nicht.' if fields.get('STATE','').startswith('HOLD') else f'Der historische Zustand lautet {v}.'
    if k == 'STATE' and v.startswith('HOLD'): return f'Der aktuelle Zustand lautet {v}; eine Freigabe ist nicht belegt.'
    if k == 'RELATION_KIND' and v == 'UNSPECIFIED': return 'Die Art der Beziehung ist unbekannt; eine Ursache lässt sich nicht ableiten.'
    if k == 'SOURCE_MISSING' and v.lower() == 'true': return 'Die Quelle fehlt; der Sachverhalt bleibt unbekannt.'
    if k == 'LYVRA' and v == 'EXTERNAL_UNCHANGED': return 'LYVRA ist ein externes, unverändertes System.'
    if k == 'CLIC_RELATION' and v == 'SEPARATE_SYSTEM': return 'CLIC ist ein separates System.'
    if k in ('SUCCESS','FAILURE') and v == 'NOT_VERIFIED': return f'{k} ist nicht verifiziert.'
    if k == 'TRANSFER' and v == 'REFERENCE_ONLY': return 'Die Übertragung dient ausschließlich als Referenz; es entsteht keine automatische Zustandsübernahme.'
    if k == 'EXPERIENCE_SOURCE': return f'Die dokumentierte Erfahrung stammt von {v.replace("CHILD_", "Child ")}.'
    if k == 'TARGET': return f'Das genannte Ziel ist {v.replace("CHILD_", "Child ")}.'
    if k == 'PARENT': return f'Das übergeordnete System ist {v}.'
    if k == 'CHILD': return f'Das Child lautet {v}.'
    if k == 'SERVICE_B' and v == 'UNAVAILABLE': return 'SERVICE_B ist nicht verfügbar; der Zustand abhängiger Dienste ist dadurch nicht belegt.'
    if v == 'NOT_VERIFIED':
        return f'{k} ist nicht verifiziert.'
    if v in ('UNKNOWN','READBACK_PENDING'):
        return f'{k} hat den ausdrücklich unsicheren Status {v}; eine Bestätigung ist nicht belegt.'
    if v in ('FALSE','FORBIDDEN'):
        return f'Für {k} gilt ausdrücklich {v}; dies darf nicht als erlaubt interpretiert werden.'
    return f'Für {k} wird {v} angegeben, ohne dass daraus weitere Tatsachen abgeleitet werden.'


def reconstruct(payload: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct from a bounded source, without executing or mutating anything.

    Each output sentence maps to the source expression which supports it.
    Unsupported notation stays literal, tagged UNKNOWN, never hallucinated.
    """
    if not isinstance(payload, dict): raise TypeError('payload must be a dict')
    source_system = payload.get('source_system')
    source_text = payload.get('source_text')
    kind = payload.get('kind')
    if not isinstance(source_system, str) or not source_system.strip() or len(source_system) > 256:
        raise ValueError('source_system must be a nonempty bounded string')
    if not isinstance(source_text, str) or not source_text.strip() or len(source_text) > MAX_SOURCE_CHARS:
        raise ValueError('source_text must be nonempty and bounded')
    if kind not in ALLOWED_KINDS: raise ValueError('unsupported source kind')
    lines = [line.strip() for line in source_text.splitlines() if line.strip()]
    fields: dict[str,str] = {}
    for line in lines:
        m = re.fullmatch(r'([A-Z][A-Z0-9_]*)\s*=\s*(.*)',line)
        if m:fields[m.group(1)] = m.group(2)
    causal_analysis = _analyze_explicit_claims(lines)
    sentences: list[str] = []
    evidence: list[dict[str,str]] = []
    for line in lines:
        m = re.fullmatch(r'([A-Z][A-Z0-9_]*)\s*=\s*(.*)',line)
        causal = _parse_causal_line(line)
        if causal:
            action, a, b = causal
            msg = {
                'CLAIM': f'Die Quelle behauptet ausdrücklich eine Ursache-Wirkung-Beziehung von {a} zu {b}; ihre Wahrheit wurde nicht unabhängig geprüft.',
                'DENY': f'Die Quelle bestreitet ausdrücklich eine Ursache-Wirkung-Beziehung von {a} zu {b}.',
                'COUNTEREXAMPLE': f'Für die behauptete Kausalbeziehung von {a} zu {b} wird ein Gegenbeispiel genannt; dessen Gültigkeit ist nicht unabhängig geprüft.',
                'HYPOTHESIS': f'Die Kausalbeziehung von {a} zu {b} ist ausdrücklich nur eine Hypothese.',
                'OBSERVE': f'Die Quelle berichtet eine Beobachtung zwischen {a} und {b}; daraus ist keine Ursache belegt.',
                'UNKNOWN': f'Ob zwischen {a} und {b} eine Ursache-Wirkung-Beziehung besteht, ist ausdrücklich unbekannt.',
            }
            s = msg[action]
            category = 'UNKNOWN' if action in ('HYPOTHESIS','UNKNOWN') else ('SOURCE_RELATION' if action in ('CLAIM','DENY','COUNTEREXAMPLE','OBSERVE') else 'UNKNOWN')
        elif m:
            s = _render_kv(m.group(1),m.group(2),fields)
            category = 'UNKNOWN' if m.group(2) in ('UNKNOWN','NOT_VERIFIED','UNSPECIFIED') else 'SOURCE_FACT'
        else:
            rel = re.fullmatch(r'([^\s→]+)\s*→\s*([^\s→]+)',line)
            dep = re.fullmatch(r'([A-Za-z][A-Za-z0-9_]*)\s+depends_on\s+([A-Za-z][A-Za-z0-9_]*)',line)
            pseudo = re.fullmatch(r'if\s+([A-Za-z_]+):\s*return\s+([A-Za-z_]+)',line)
            if rel:
                s = f'Zwischen {rel.group(1)} und {rel.group(2)} ist eine gerichtete Beziehung angegeben; ob diese kausal ist, bleibt unbekannt.'
                category = 'SOURCE_RELATION'
            elif dep:
                s = f'{dep.group(1)} hängt von {dep.group(2)} ab; ein Ausfall von {dep.group(1)} ist nicht belegt.'
                category = 'SOURCE_RELATION'
            elif pseudo:
                s = f'Die bedingte Anweisung sieht bei {pseudo.group(1)} den Rückgabewert {pseudo.group(2)} vor; sie wurde nicht ausgeführt.'
                category = 'SOURCE_FACT'
            else:
                s = f'Die weitere Quellnotation „{line}“ bleibt ohne zusätzliche Interpretation erhalten.'
                category = 'UNKNOWN'
        sentences.append(s)
        evidence.append({'source_span':line,'output_span':s,'evidence_class':category})
    try:
        from .causal_graph_r04 import build_graph
    except ImportError:
        # The frozen R01 contract driver imports this module directly by file path.
        import importlib.util
        from pathlib import Path
        sibling = Path(__file__).with_name("causal_graph_r04.py")
        spec = importlib.util.spec_from_file_location("cures_graph_r04", sibling)
        graph_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(graph_module)
        build_graph = graph_module.build_graph
    graph = build_graph(causal_analysis)
    return {
        'schema': '666CURES_RECONSTRUCTION_JSON_R04_V1',
        'graph': graph,
        'fulltext':' '.join(sentences),
        'source_system':source_system,
        'preserved_identity':source_system,
        'evidence_map':evidence,
        'inferred_claims':[],
        'authority_changed':False,
        'mutations':[],
        'causal_analysis': causal_analysis,
    }


# R03 additive, strictly declarative notation. No inference from adjacency,
# relation arrows, source ordering, or transitive chains.
_CAUSAL = re.compile(r'^(CLAIM|DENY|COUNTEREXAMPLE|HYPOTHESIS|OBSERVE|UNKNOWN)\s+CAUSE\s+([A-Za-z][A-Za-z0-9_.-]*)\s*->\s*([A-Za-z][A-Za-z0-9_.-]*)$')

def _parse_causal_line(line: str):
    found = _CAUSAL.fullmatch(line)
    return found.groups() if found else None

def _analyze_explicit_claims(lines: list[str]) -> dict[str, Any]:
    """Bounded, provenance-first account of assertions, not a truth engine."""
    records: dict[tuple[str,str], dict[str, Any]] = {}
    status_values: dict[str, list[dict[str, Any]]] = {}
    for index, line in enumerate(lines, start=1):
        ca = _parse_causal_line(line)
        if ca:
            typ, src, target = ca
            key = src, target
            rec = records.setdefault(key, {'source':src,'target':target,'evidence':[]})
            rec['evidence'].append({'line':index,'source_span':line,'assertion':typ})
        kv = re.fullmatch(r'([A-Z][A-Z0-9_]*)\s*=\s*(.*)', line)
        if kv:
            status_values.setdefault(kv.group(1), []).append({'value':kv.group(2),'line':index,'source_span':line})
    relationships=[]
    for rec in records.values():
        types={e['assertion'] for e in rec['evidence']}
        opposed=bool(types.intersection({'DENY','COUNTEREXAMPLE'}))
        claimed='CLAIM' in types
        rec['assessment'] = ('CONTRADICTED_SOURCE_ASSERTIONS' if claimed and opposed else
                             'SOURCE_CLAIM_UNVERIFIED' if claimed else
                             'SOURCE_DENIAL_OR_COUNTEREXAMPLE' if opposed else
                             'HYPOTHESIS_ONLY' if 'HYPOTHESIS' in types else
                             'OBSERVATION_NOT_CAUSATION' if 'OBSERVE' in types else
                             'UNKNOWN')
        rec['independently_verified']=False
        relationships.append(rec)
    conflicts=[]
    for key, vals in status_values.items():
        if len({v['value'] for v in vals})>1:
            conflicts.append({'field':key,'values':vals,'assessment':'CONFLICT_UNRESOLVED'})
    return {'status':'SOURCE_ASSERTIONS_ONLY_NO_CAUSAL_VERIFICATION',
            'relationships':relationships,'field_conflicts':conflicts,
            'transitive_causation_inferred':False,'independent_validation':False}


# Additive R05 entrypoint, no changes to R01-R04 reconstruct behavior.
def reconstruct_sources(payload: dict[str, Any]) -> dict[str, Any]:
    """R05 opt-in cross-document, declarative JSON transport (no CLS execution)."""
    if not isinstance(payload, dict): raise TypeError("payload must be an object")
    if set(payload) - {"documents"}: raise ValueError("unsupported R05 top-level field")
    try:
        from .evidence_graph_r05 import evaluate_documents
    except ImportError:
        import importlib.util
        from pathlib import Path
        spec=importlib.util.spec_from_file_location("cures_graph_r05",Path(__file__).with_name("evidence_graph_r05.py"))
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        evaluate_documents=module.evaluate_documents
    return evaluate_documents(payload.get("documents"))
