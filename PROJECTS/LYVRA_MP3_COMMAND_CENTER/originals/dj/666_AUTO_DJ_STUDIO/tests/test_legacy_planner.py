import importlib.util
from pathlib import Path
import random
import unittest

spec = importlib.util.spec_from_file_location('legacy_planner',Path(__file__).resolve().parents[1]/'engine'/'legacy_planner.py')
import sys
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

class LegacyPlannerTests(unittest.TestCase):
    def test_clean_title_r03_tokens(self):
        self.assertEqual(mod.clean_title('001_Deep-Dark FINAL V3 (2)'), 'Deep Dark')
    def test_family_variants(self):
        self.assertEqual(mod.family_name('012_Neon-Acid (2) FINAL'), mod.family_name('Neon Acid'))
    def test_artist(self):
        self.assertEqual(mod.artist_name('Fraggle - Hard Psycho'), 'fraggle')
    def test_energy_precedence(self):
        self.assertEqual(mod.energy_bucket('dark chill'), 'LOW')
        self.assertEqual(mod.energy_bucket('dark pressure'), 'HIGH')
    def test_reproducible_catalog(self):
        items=[(Path(f'{i}_Deep-Dark ({i}).wav'), 180) for i in range(1,5)]
        self.assertEqual(mod.catalog(items,random.Random(4)), mod.catalog(items,random.Random(4)))
    def test_tracks_split_count(self):
        members=mod.catalog([(Path(f'{i}_track.wav'),60) for i in range(9)],random.Random(3))
        blocks=mod.balanced_blocks(members,'TRACKS',target_tracks=4)
        self.assertEqual(len(blocks),3)
        self.assertEqual(sum(b.total_tracks for b in blocks),9)
    def test_hybrid_split(self):
        members=mod.catalog([(Path(f'track_{i}.wav'),60) for i in range(5)],random.Random(1))
        self.assertEqual(len(mod.balanced_blocks(members,'HYBRID',target_minutes=2,target_tracks=10)),3)
    def test_variant_avoidance(self):
        members=mod.catalog([(Path(f'Neon ( {i} ).wav'),120) for i in range(4)],random.Random(2))
        blocks=mod.balanced_blocks(members,'TRACKS',target_tracks=1)
        self.assertEqual(len(blocks),4)
    def test_hardcore_no_loss(self):
        inputs=[(Path(x+'.wav'),120) for x in ('ambient intro','dark pressure','middle','fraggle - chill','other')]
        members=[m for group in mod.catalog(inputs,random.Random(2)) for m in group]
        actual=mod.smart_shuffle(members,True)
        self.assertEqual(set(actual),set(members))
    def test_empty(self):
        self.assertEqual(mod.balanced_blocks([]),[])
    def test_invalid_mode(self):
        with self.assertRaises(ValueError):mod.balanced_blocks([[mod.Member(Path('x'),1,'x','x','MID')]],'BAD')
    def test_invalid_duration(self):
        with self.assertRaises(ValueError):mod.catalog([(Path('x'),float('nan'))])
    def test_all_unique_after_distribution(self):
        entries=[(Path(f'{i}_x.wav'),60) for i in range(20)]
        groups=mod.catalog(entries,random.Random(5))
        blocks=mod.balanced_blocks(groups,'TRACKS',target_tracks=3)
        self.assertEqual({m.path for b in blocks for m in b.items},{p for p,d in entries})

if __name__ == '__main__':unittest.main()
