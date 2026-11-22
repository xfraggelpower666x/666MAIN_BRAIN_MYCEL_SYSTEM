import importlib.util,random,sys,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('legacy_planner',Path(__file__).resolve().parents[1]/'engine'/'legacy_planner.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class PlannerTests(unittest.TestCase):
 def test_title(self):self.assertEqual(m.clean_title('001_Deep-Dark FINAL V3 (2)'),'Deep Dark')
 def test_family(self):self.assertEqual(m.family_name('012_Neon-Acid (2) FINAL'),m.family_name('Neon Acid'))
 def test_artist(self):self.assertEqual(m.artist_name('Fraggle - Hard Psycho'),'fraggle')
 def test_energy(self):
  self.assertEqual(m.energy_bucket('dark chill'),'LOW')
  self.assertEqual(m.energy_bucket('dark pressure'),'HIGH')
 def test_catalog_repeatable(self):
  data=[(Path(f'{i}_Track.wav'),180) for i in range(9)]
  self.assertEqual(m.catalog(data,random.Random(4)),m.catalog(data,random.Random(4)))
 def test_tracks_split(self):
  families=m.catalog([(Path(f'{i}_Track.wav'),60) for i in range(9)],random.Random(3))
  blocks=m.balanced_blocks(families,'TRACKS',target_tracks=4)
  self.assertEqual(len(blocks),3);self.assertEqual(sum(x.total_tracks for x in blocks),9)
 def test_hybrid_split(self):
  families=m.catalog([(Path(f'track_{i}.wav'),60) for i in range(5)],random.Random(1))
  self.assertEqual(len(m.balanced_blocks(families,'HYBRID',target_minutes=2,target_tracks=10)),3)
 def test_no_drops(self):
  data=[(Path(f'{i}_x.wav'),60) for i in range(20)]
  blocks=m.balanced_blocks(m.catalog(data,random.Random(5)),'TRACKS',target_tracks=3)
  self.assertEqual({x.path for b in blocks for x in b.items},{p for p,d in data})
 def test_hardcore_no_drops(self):
  data=[(Path(s+'.wav'),100) for s in ['ambient intro','dark pressure','middle','fraggle - chill','other']]
  items=[mbr for family in m.catalog(data,random.Random(2)) for mbr in family]
  self.assertEqual(set(m.smart_shuffle(items,True)),set(items))
 def test_empty(self):self.assertEqual(m.balanced_blocks([]),[])
 def test_bad_mode(self):
  with self.assertRaises(ValueError):m.balanced_blocks([],split_mode='INVALID')
 def test_bad_duration(self):
  with self.assertRaises(ValueError):m.catalog([(Path('x'),float('nan'))])
 def test_short_order_unchanged(self):
  items=[m.Member(Path('a'),1,'a','a','MID')]
  self.assertEqual(m.smart_shuffle(items,True),items)
 def test_families_spread(self):
  data=[(Path(f'Song ({i}).mp3'),90) for i in range(4)]
  blocks=m.balanced_blocks(m.catalog(data,random.Random(1)),'TRACKS',target_tracks=1)
  self.assertEqual(len(blocks),4)
if __name__=='__main__':unittest.main()
