"""Finite Morse flashing plan; preview-only, never changes Caps Lock.

Independent encoding of International Morse alphabet. No third-party code.
"""
from dataclasses import dataclass

MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....',
    '7': '--...', '8': '---..', '9': '----.', ' ': ' ',
}


@dataclass(frozen=True)
class Pulse:
    on: bool
    ms: int


def encode(text: str, unit_ms: int = 120):
    """Return immutable on/off pulses, standard 1/3/7-unit gaps."""
    if not isinstance(text, str) or not text or len(text) > 120:
        raise ValueError('text length must be 1..120')
    if type(unit_ms) is not int or not 30 <= unit_ms <= 1000:
        raise ValueError('unit_ms must be 30..1000')
    if any(ch not in MORSE for ch in text.upper()):
        raise ValueError('unsupported Morse character')
    words = text.upper().split(' ')
    output = []
    for wi, word in enumerate(words):
        if wi and word:
            output.append(Pulse(False, 7 * unit_ms))
        for ci, ch in enumerate(word):
            if ci:
                output.append(Pulse(False, 3 * unit_ms))
            for si, mark in enumerate(MORSE[ch]):
                if si:
                    output.append(Pulse(False, unit_ms))
                output.append(Pulse(True, (1 if mark == '.' else 3) * unit_ms))
    return tuple(output)
