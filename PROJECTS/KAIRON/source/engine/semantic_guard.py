"""R19.8: track-local output review; no renderer or automatic rewriting."""
import re
from . import semantic_reinforcement as original
from . import semantic_intelligence as semantic

BOUNDARY = re.compile(r'[.!?;,\n]+|\b(?:but|however|instead|rather|yet|sondern|aber|jedoch|stattdessen|hingegen)\b', re.I)


def occurrences(text, anchor):
    """Exact positive occurrences, with negation scoped to each occurrence."""
    start = 0
    for boundary in list(BOUNDARY.finditer(text)) + [None]:
        end = boundary.start() if boundary else len(text)
        clause = text[start:end]
        for match in re.finditer(r'(?<!\w)' + re.escape(anchor) + r'(?!\w)', clause, re.I):
            words = re.findall(r'[\wäöüß]+', clause[:match.start()].casefold())[-5:]
            if not any(w in semantic.NEGATORS for w in words):
                yield start + match.start(), start + match.end()
        if boundary:
            start = boundary.end()


def reviewed_variant(text, bindings, budget):
    """Only approved positive exact spans and semantically matching symbols."""
    spans = []
    for binding in bindings:
        a, b = binding['start'], binding['end']
        anchor = binding['anchor']
        symbols = [s for term, s, _ in original.RELATIONS if term == anchor.casefold()]
        if not any(binding['symbol'] == s*n for s in symbols for n in range(1,9)):
            raise ValueError('SYMBOL_ANCHOR_MISMATCH')
        if (a,b) not in occurrences(text, anchor):
            raise ValueError('NONPOSITIVE_OR_STALE_SPAN')
        if any(a < y and x < b for x,y in spans):
            raise ValueError('OVERLAPPING_BINDINGS')
        spans.append((a,b))
    return original.apply_reviewed_bindings(text, bindings, budget)


def review(fields, intent):
    analysis = original.assess(intent)
    checks = []
    # Each positive occurrence is checked, not merely any symbol on the line.
    for target, names in original.FIELDS.items():
        for name in names:
            value = intent.get(name) or ''
            if not isinstance(value,str):
                continue
            for anchor, symbol, job in original.RELATIONS:
                for a,b in occurrences(value,anchor):
                    present = value[b:].lstrip().startswith(symbol)
                    checks.append(dict(field=target,source_field=name,anchor=anchor,start=a,end=b,
                        symbol=symbol,function=job,review_required=not present))
    lyrics = fields['lyrics']['text']
    ending = original.lyric_relations(lyrics)
    # Bracketed vocal instructions after terminal marker still require human review.
    commands = [r['line'] for r in ending['rows'] if r['after_vocal_end'] and r['role']=='COMMAND'
                and not re.search(r'all vocals end here|no vocals|instrumental only',r['text'],re.I)
                and re.search(r'\b(?:vocal|vocals|sing|singing|choir|chant|whisper|spoken|echo)\b',r['text'],re.I)]
    ending['post_end_command_review'] = commands
    ending['review_required'] = ending['review_required'] or bool(commands)
    return dict(status='CREATOR_REVIEW' if any(c['review_required'] for c in checks) or ending['review_required'] else 'CANDIDATE_CHECK_COMPLETE',
                checks=checks, lyric_relations=ending, musical_context=analysis,
                no_automatic_rewrite=True,no_render_guarantee=True)
