"""Bounded, simulation-only scheduler with explicit animation arbitration.

LED patterns cannot fight existing monitor rules or user key presses because
this module does not connect to a live backend. Physical writes are forbidden.
"""
from dataclasses import dataclass
from .patterns import Frame


@dataclass(frozen=True)
class PreviewResult:
    frames: tuple[Frame, ...]
    total_ms: int
    destination: str = 'preview'


def prepare(frames, max_frames=4096, max_total_ms=600000):
    if type(max_frames) is not int or max_frames < 1:
        raise ValueError('invalid frame limit')
    if type(max_total_ms) is not int or max_total_ms < 1:
        raise ValueError('invalid duration limit')
    result = tuple(frames)
    if not result or len(result) > max_frames or any(not isinstance(f, Frame) for f in result):
        raise ValueError('invalid frame sequence')
    total = sum(f.duration_ms for f in result)
    if total > max_total_ms:
        raise ValueError('preview duration limit exceeded')
    return PreviewResult(result, total)


def morse_frames(pulses, led='caps'):
    if led not in {'caps', 'num', 'scroll'}:
        raise ValueError('unknown indicator')
    frames = []
    for pulse in pulses:
        if type(pulse.on) is not bool or type(pulse.ms) is not int or pulse.ms < 20:
            raise ValueError('invalid Morse pulse')
        states = {name: False for name in ('num','caps','scroll')}
        states[led] = pulse.on
        frames.append(Frame(**states, duration_ms=pulse.ms))
    return tuple(frames)
