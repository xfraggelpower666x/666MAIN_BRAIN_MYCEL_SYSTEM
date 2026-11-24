"""Behavioral port of the R03 PowerShell variant/block planning algorithms.

Scope: planning only; no conversion, file mutation, or audio-quality claims.
Original: tool.ps1 Get-FamilyName, Get-ArtistName, Get-EnergyBucket,
Build-VariantCatalog, Build-BalancedPlaylistBlocks, Optimize-BlockOrder[Hardcore].
"""
from dataclasses import dataclass, field
import math
import random
import re
from pathlib import Path
from typing import Sequence

AUDIO_EXTENSIONS = frozenset({'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.opus', '.wma'})


def clean_title(value: str) -> str:
    clean = re.sub(r'^\d+[\s_.-]*', '', value)
    clean = re.sub(r'\s*\(\d+\)', '', clean)
    clean = re.sub(r'\bV\d+\b|\bFINAL\b|\bMIXDOWN\b|\bTEMP\b|\bDRAFT\b', '', clean, flags=re.I)
    clean = re.sub(r'[_-]+', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean or value


def family_name(name: str) -> str:
    return clean_title(re.sub(r'\s*\(\d+\)', '', name)).lower()


def artist_name(name: str) -> str:
    name = name.lower()
    match = re.match(r'^\s*(.+?)\s*-\s*', name)
    if match:
        return match.group(1).strip()
    words = name.split()
    return ' '.join(words[:2]) if len(words) >= 2 else name


def energy_bucket(name: str) -> str:
    lowered = name.lower()
    if re.search(r'intro|ambient|soft|calm|downtempo|chill', lowered):
        return 'LOW'
    if re.search(r'hard|peak|pressure|freak|destroy|dark|psy|acid|rage', lowered):
        return 'HIGH'
    return 'MID'


@dataclass(frozen=True)
class Member:
    path: Path
    duration_seconds: float
    family: str
    artist: str
    energy: str


@dataclass
class Block:
    index: int
    items: list[Member] = field(default_factory=list)
    families: set[str] = field(default_factory=set)
    total_seconds: float = 0

    def append(self, member: Member) -> None:
        self.items.append(member)
        self.families.add(member.family)
        self.total_seconds += member.duration_seconds

    @property
    def total_tracks(self) -> int:
        return len(self.items)


def catalog(entries: Sequence[tuple[Path, float]], rng: random.Random | None = None) -> list[list[Member]]:
    """Like R03: group variants by cleaned family, shuffle members and families."""
    rng = rng or random.Random()
    groups: dict[str, list[Member]] = {}
    for path, duration in entries:
        path = Path(path)
        if not math.isfinite(duration) or duration < 0:
            raise ValueError('Invalid audio duration')
        title = path.stem
        family = family_name(title)
        groups.setdefault(family, []).append(Member(path, float(duration), family, artist_name(title), energy_bucket(title)))
    families = list(groups.values())
    for members in families:
        rng.shuffle(members)
    rng.shuffle(families)
    return families


def balanced_blocks(families: Sequence[Sequence[Member]], split_mode: str = 'MINUTES', target_minutes: int = 180, target_tracks: int = 40) -> list[Block]:
    if split_mode not in ('MINUTES', 'TRACKS', 'HYBRID'):
        raise ValueError('Unknown split mode')
    all_items = [m for members in families for m in members]
    if not all_items:
        return []
    seconds = sum(m.duration_seconds for m in all_items)
    by_min = math.ceil(seconds / (target_minutes * 60)) if target_minutes > 0 else 1
    by_tracks = math.ceil(len(all_items) / target_tracks) if target_tracks > 0 else 1
    count = max(1, by_min if split_mode == 'MINUTES' else by_tracks if split_mode == 'TRACKS' else max(by_min, by_tracks))
    # At most one block per item avoids unbounded allocation on malformed duration metadata.
    count = min(count, len(all_items))
    blocks = [Block(i + 1) for i in range(count)]
    pointer = 0
    for members in families:
        for member in members:
            assigned = False
            for shift in range(count):
                idx = (pointer + shift) % count
                if member.family not in blocks[idx].families:
                    blocks[idx].append(member)
                    pointer = (idx + 1) % count
                    assigned = True
                    break
            if not assigned:
                block = min(blocks, key=lambda b: (b.total_tracks, b.total_seconds))
                block.append(member)
    return blocks


def smart_shuffle(items: Sequence[Member], hardcore: bool = False) -> list[Member]:
    remaining = list(items)
    if len(remaining) <= 2:
        return remaining
    ordered = []
    last_family = ''
    last_artist = ''
    cycle = ('LOW', 'MID', 'HIGH', 'MID')
    while remaining:
        candidate = None
        if hardcore:
            desired = cycle[len(ordered) % len(cycle)]
            candidate = next((i for i, m in enumerate(remaining) if m.family != last_family and m.artist != last_artist and m.energy == desired), None)
            if candidate is None:
                candidate = next((i for i, m in enumerate(remaining) if m.family != last_family and m.artist != last_artist), None)
        if candidate is None:
            candidate = next((i for i, m in enumerate(remaining) if m.family != last_family), 0)
        picked = remaining.pop(candidate)
        ordered.append(picked)
        last_family, last_artist = picked.family, picked.artist
    return ordered
