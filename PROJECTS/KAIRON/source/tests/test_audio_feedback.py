import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np,soundfile as sf
from engine import audio_feedback as a,portable as p,relational as r

class AudioFeedbackTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.dir=Path(self.temp.name);(self.dir/'tracks').mkdir()
  self.patcher=patch.object(p,'DATA',self.dir);self.patcher.start();self.addCleanup(self.patcher.stop)
  sr=16000;t=np.arange(sr*2)/sr
  self.wav=self.dir/'mix.wav';sf.write(self.wav,(0.4*np.sin(2*np.pi*110*t)).astype(np.float32),sr)
  self.wav2=self.dir/'voice.wav';sf.write(self.wav2,(0.2*np.sin(2*np.pi*900*t)).astype(np.float32),sr)
  p.atomic(self.dir/'tracks'/'unit.json',{'track_id':'unit','motor':'rolling bass','target_seconds':3})
 def test_real_measure(self):
  x=a.measure(self.wav);self.assertEqual(x['duration_s'],2.0);self.assertEqual(x['evidence_type'],'MEASURED_AUDIO');self.assertEqual(len(x['artifact_sha256']),64)
 def test_band_role(self):
  x=a.measure(self.wav);self.assertGreater(x['band_energy_ratio']['low_20_180'],0.95)
 def test_no_invented_loudness_or_bpm(self):
  x=a.measure(self.wav);self.assertNotIn('bpm',x);self.assertIn('NOT_EBU_R128_LOUDNESS',x['limitations'])
 def test_duration_comparison(self):
  x=a.compare('unit','suno',self.wav,tolerance_seconds=.5);self.assertEqual(x['findings'][0]['status'],'MEASURED_DEVIATION');self.assertEqual(x['causal_status'],'UNKNOWN_REQUIRES_HUMAN_AND_CONTROLLED_EXPERIMENT')
 def test_stem_screening_not_masking(self):
  x=a.compare('unit','suno',self.wav,{'bass':self.wav,'voice':self.wav2});self.assertFalse(x['findings'][-1]['masking_confirmed'])
 def test_stem_mismatch(self):
  x=self.dir/'short.wav';sf.write(x,np.zeros(400,dtype=np.float32),16000)
  with self.assertRaises(a.AudioError):a.compare('unit','suno',self.wav,{'bad':x})
 def test_missing_file(self):
  with self.assertRaises(a.AudioError):a.measure(self.dir/'missing.wav')
 def test_no_fake_artifact(self):
  with self.assertRaises(a.AudioError):a.measure(self.dir/'fake.wav')
 def test_track_guard(self):
  with self.assertRaises(r.GraphError):a.compare('../invalid','suno',self.wav)
 def test_record_and_idempotent(self):
  x=a.compare('unit','suno',self.wav);self.assertEqual(a.record(x)['status'],'LOCALLY_RECORDED_PROVISIONAL');self.assertEqual(a.record(x)['status'],'ALREADY_RECORDED')
 def test_review_no_global(self):
  x=a.compare('unit','suno',self.wav);a.record(x); y=a.review('unit',x['id'],'UNKNOWN','creator','needs controlled test');self.assertFalse(y['global_rule'])
 def test_review_requires_evidence(self):
  x=a.compare('unit','suno',self.wav);a.record(x)
  with self.assertRaises(a.AudioError):a.review('unit',x['id'],'DESIGN_FAILURE','', 'guess')
 def test_no_foreign_authority(self):
  x=a.compare('unit','suno',self.wav);self.assertEqual(x['system_id'],'666TDI-001');self.assertFalse(x['external_repo_write'])
 def test_rehydrate_tampering(self):
  x=a.compare('unit','suno',self.wav);a.record(x)
  y=p.load(self.dir/'audio_feedback'/f"{x['id']}.json");y['causal_status']='CONFIRMED';p.atomic(self.dir/'audio_feedback'/f"{x['id']}.json",y)
  self.assertEqual(a.rehydrate()['status'],'PARTIAL')
 def test_audio_error_on_unsupported(self):
  f=self.dir/'stuff.mp3';f.write_bytes(b'bad')
  with self.assertRaises(a.AudioError):a.measure(f)
if __name__=='__main__':unittest.main()
