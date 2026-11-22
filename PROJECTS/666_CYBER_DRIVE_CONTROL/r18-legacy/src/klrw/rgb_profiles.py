"""Offline RGB profile validator. Never sends HID or vendor commands."""
import json
import re
from dataclasses import dataclass

HEX = re.compile(r'^[0-9a-fA-F]{6}$')

@dataclass(frozen=True)
class RgbProfile:
    keys: tuple[tuple[int, str], ...]

    def as_dict(self):
        return {str(i): color for i, color in self.keys}

def parse_profile(payload, max_index=124):
    if not isinstance(max_index, int) or isinstance(max_index,bool) or max_index < 0 or max_index > 4096:
        raise ValueError('Invalid max_index')
    if isinstance(payload, str):
        def unique(pairs):
            result = {}
            for k,v in pairs:
                if k in result: raise ValueError('Duplicate index')
                result[k] = v
            return result
        payload = json.loads(payload, object_pairs_hook=unique)
    if not isinstance(payload, dict):
        raise ValueError('Expected JSON object')
    if len(payload) > max_index+1: raise ValueError('Too many keys')
    entries = []
    for key, color in payload.items():
        if not isinstance(key, str) or not key.isascii() or not key.isdecimal() or str(int(key)) != key:
            raise ValueError('Invalid key index')
        i = int(key)
        if i > max_index: raise ValueError('Index exceeds configured limit')
        if not isinstance(color, str) or HEX.fullmatch(color) is None:
            raise ValueError('Color must be six hexadecimal digits')
        entries.append((i, '#' + color.lower()))
    return RgbProfile(tuple(sorted(entries)))
