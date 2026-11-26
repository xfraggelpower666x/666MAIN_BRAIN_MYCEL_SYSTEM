"""KAIRON: advisory radial arrangement, no rendering or automatic persistence."""
def arrange(report):
    if report.get('system_id') != '666TDI-001':
        raise ValueError('FOREIGN_IDENTITY')
    if not report.get('mandala_candidate'):
        return None
    positive=report['signal_evidence']; negative=report['negated_signals']
    active={k for k,v in positive.items() if v and not negative.get(k)}
    if 'MANTRA' not in active or not active.intersection({'SPACE','DYNAMICS'}):
        return None
    roles=[('CENTER', ('MANTRA',)), ('INNER', ('MOTION','VOICE')), ('MIDDLE', ('DYNAMICS','FX')), ('OUTER', ('SPACE',))]
    return {'status':'REVIEW_ONLY','rings':[{'ring':name,'functions':[k for k in keys if k in active]} for name,keys in roles], 'gates':['BUILD','BREAK','RETURN'] if 'DYNAMICS' in active else [], 'low_stable':True,'audio_measured':False,'automatic_promotion':False}
