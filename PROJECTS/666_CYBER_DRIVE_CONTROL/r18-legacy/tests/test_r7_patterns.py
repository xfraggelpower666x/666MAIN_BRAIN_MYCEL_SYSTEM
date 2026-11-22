import pytest
from klrw.patterns import Frame, sequence, meter
from klrw.morse_preview import encode
from klrw.preview_scheduler import prepare, morse_frames
from klrw.animations_cli import main


def test_chase():
    assert [f.states() for f in sequence('chase')] == [
        {'num': True, 'caps': False, 'scroll': False},
        {'num': False, 'caps': True, 'scroll': False},
        {'num': False, 'caps': False, 'scroll': True},
    ]

@pytest.mark.parametrize('name,count', [('bounce',4),('fill',6),('center',4),('pulse',3)])
def test_patterns(name,count):
    assert len(sequence(name)) == count

@pytest.mark.parametrize('value,n', [(0,0),(1,1),(33,1),(34,2),(67,3),(100,3),(150,3)])
def test_meter(value,n):
    assert sum(meter(value).states().values()) == n

def test_meter_bad():
    with pytest.raises(ValueError): meter(float('nan'))
    with pytest.raises(ValueError): meter(4, 0)

def test_pattern_bad():
    with pytest.raises(ValueError): sequence('unknown')
    with pytest.raises(ValueError): sequence('chase', 0)
    with pytest.raises(ValueError): Frame(True, 0, False)

def test_morse_sos():
    assert [p.ms for p in encode('SOS', 100) if p.on] == [100,100,100,300,300,300,100,100,100]
    assert all(not p.on for p in encode('A B', 100) if p.ms==700)

def test_morse_bad():
    with pytest.raises(ValueError): encode('é')
    with pytest.raises(ValueError): encode('')
    with pytest.raises(ValueError): encode('HI', 1)

def test_prepare_bounds():
    assert prepare(sequence('chase')).destination == 'preview'
    with pytest.raises(ValueError): prepare([])
    with pytest.raises(ValueError): prepare(sequence('chase'), max_frames=2)
    with pytest.raises(ValueError): prepare(sequence('chase'), max_total_ms=300)

def test_morse_mapping():
    frames = morse_frames(encode('E', 50), 'scroll')
    assert frames[0].scroll and not frames[0].num and not frames[0].caps
    with pytest.raises(ValueError): morse_frames(encode('E'), 'foo')

def test_cli_pattern(capsys):
    assert main(['pattern','chase']) == 0
    assert '"destination": "preview"' in capsys.readouterr().out

def test_cli_meter(capsys):
    assert main(['meter','50']) == 0
    assert '"total_ms": 150' in capsys.readouterr().out

def test_cli_morse(capsys):
    assert main(['morse','SOS']) == 0
    assert '"frames"' in capsys.readouterr().out
