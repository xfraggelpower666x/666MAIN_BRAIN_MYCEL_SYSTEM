"""KAIRON R20.9: context GAT and reusable arrangement candidates.

Reads musical creator input; never silently registers a preset, replaces lyrics,
activates foreign plugins or claims to hear audio. A musical-function extension
of the existing track analysis, not a second compositional authority.
"""
from __future__ import annotations
import re

SIGNALS = {
    'MANTRA': ('mantra', 'ritual', 'chant', 'affirmation', 'mantra', 'ich bin', 'inner core'),
    'MOTION': ('rolling bass', 'forward motion', 'psy bass', 'psybass', '4/4', 'marching'),
    'SPACE': ('orbit', 'stereo', 'whisper', 'echo', 'spatial', 'space', 'reverb'),
    'FX': ('acid', '303', 'glitch', 'stutter', 'reverse reverb', 'sfx', 'filter'),
    'DYNAMICS': ('drop', 'break', 'silence', 'build', 'fake end', 'tension', 'release'),
    'VOICE': ('vocal', 'voice', 'lyrics', 'mantra', 'whisper', 'spoken'),
    'ENDING': ('final hit', 'ending', 'outro', 'silence', 'last hit', 'endguard'),
}
# Context-specific relations; no default gimmicks or generated modules.
RELATIONS = (
    ('VOICE', 'FX', 'VOICE_FX_MASKING_RISK', 'Separate vocal clarity and high-density acid/glitch in time or spectral space'),
    ('MOTION', 'SPACE', 'LOW_STABILITY_VS_STEREO_MOVEMENT', 'Keep kick/sub phase stable and move only higher perceptual layers'),
    ('MANTRA', 'DYNAMICS', 'MANTRA_DYNAMICS_RELATION', 'Use repetition intentionally with varying tension and release'),
)


def _terms(text: str, terms: tuple[str, ...]) -> list[str]:
    matches=[]
    for phrase in terms:
        if re.search(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)', text, flags=re.I):
            matches.append(phrase)
    return sorted(set(matches))


def evaluate(track: dict) -> dict:
    """Return read-only candidates for the existing track, never save or promote.

    No cross-system evidence, no global learning, no inference of measured audio.
    """
    if not isinstance(track, dict):
        raise ValueError('INVALID_TRACK')
    if track.get('system_id') not in (None, '666TDI-001'):
        raise ValueError('FOREIGN_IDENTITY')
    fields=('lyrics','story','motor','mid','high','atmosphere','psychoacoustics','structure','ending','genre','voice')
    for field in fields:
        if not isinstance(track.get(field,''),str):
            raise ValueError('INVALID_FIELD:'+field)
    text=' '.join(track.get(k,'') for k in fields).lower()
    # Avoid requirements cannot be treated as positive evidence. Explicit negative
    # clauses are excluded; ambiguous complex negations remain human-review.
    clauses=re.split(r'[,;\n.]|\bbut\b|\baber\b',text)
    positives=[]
    negatives=[]
    for clause in clauses:
        if re.search(r'\b(?:avoid|without|no|not|kein|keine|ohne|vermeide)\b',clause):
            negatives.append(clause)
        else:
            positives.append(clause)
    positive=' '.join(positives)
    denied=' '.join(negatives)
    evidence={key:_terms(positive,terms) for key,terms in SIGNALS.items()}
    excluded={key:_terms(denied,terms) for key,terms in SIGNALS.items()}
    active={k for k,v in evidence.items() if v}
    relations=[{'relation':name,'from':a,'to':b,'impact':advice,'status':'CAUSAL_HYPOTHESIS'}
               for a,b,name,advice in RELATIONS if a in active and b in active]
    # A preset requires independently reusable structure, FX and dynamics.
    candidate = {'genre':track.get('genre',''), 'bpm':track.get('bpm'),
                 'functional_bundles':sorted(active),
                 'replaceable_lyrics':True, 'lyrics_embedded':False,
                 'status':'REVIEW_ONLY', 'creator_approval_required':True,
                 'persistent_registration':False}
    evidence_count=sum(bool(v) for v in evidence.values())
    if not text.strip(): classification='REFERENCE_ONLY'
    elif {'FX','DYNAMICS','MOTION'}.issubset(active) and evidence_count>=4: classification='PRESET_CANDIDATE'
    else: classification='TRACK_ONLY'
    mandala = bool('MANTRA' in active and {'SPACE','DYNAMICS'} & active)
    return {'schema':'KAIRON_CONTEXT_GAT_R209','system_id':'666TDI-001',
            'classification':classification,'signal_evidence':evidence,
            'negated_signals':excluded,'functional_relations':relations,
            'mandala_candidate':mandala,'mandala_status':'REVIEW_ONLY' if mandala else 'NOT_SELECTED',
            'preset_candidate':candidate if classification=='PRESET_CANDIDATE' else None,
            'source_lyrics_preserved':True,'audio_measured':False,
            'module_auto_install':False,'preset_auto_save':False,
            'foreign_authority':'REFERENCE_ONLY',
            'limitations':['NO_AUDIO_MEASUREMENT','NO_AUTOMATIC_GLOBAL_LEARNING',
                           'COMPLEX_NEGATIONS_REQUIRE_REVIEW']}
