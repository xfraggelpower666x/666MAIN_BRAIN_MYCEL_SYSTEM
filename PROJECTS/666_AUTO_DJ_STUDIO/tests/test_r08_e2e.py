"""R08 non-destructive regression and optional real local FFmpeg smoke test."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'engine'))
from legacy_media import CoverRotation, metadata_ffmpeg_args, metadata_profile
from master_export import export_stream_ready

class R08Contracts(unittest.TestCase):
    def test_cover_rotation_no_duplicates_before_cycle(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for n in ('a.jpg','b.png','c.webp'):(p/n).write_bytes(b'no need to decode')
            pool=CoverRotation(p,seed=2)
            self.assertEqual(len({pool.next().name for _ in range(3)}),3)
            self.assertIsNotNone(pool.next())

    def test_metadata_allowlist_and_title(self):
        profile=metadata_profile({'write_metadata':True,'metadata':{'artist':'Artist R08'}})
        args=metadata_ffmpeg_args(profile,'Audio Title')
        self.assertIn('artist=Artist R08',args)
        self.assertIn('title=Audio Title',args)
        with self.assertRaises(ValueError):metadata_profile({'write_metadata':True,'metadata':{'x':'bad'}})

    def test_stream_ready_preserves_previous(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); block=root/'BLOCK_001';block.mkdir()
            (block/'sample.mp3').write_bytes(b'audio')
            (block/'AUTO_DJ_EXPORT.m3u').write_text('#EXTM3U\nsample.mp3\n')
            old=root/'STREAM_READY';old.mkdir();(old/'user-file.txt').write_text('KEEP')
            out,prev=export_stream_ready(root,[block])
            self.assertEqual((out/'master.m3u').read_text(encoding='utf-8-sig'),'#EXTM3U\nBLOCK_001/sample.mp3\n')
            self.assertEqual((prev/'user-file.txt').read_text(),'KEEP')

    def test_stream_ready_rejects_unsafe_playlist_without_touching_previous(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);block=root/'BLOCK_001';block.mkdir()
            (block/'AUTO_DJ_EXPORT.m3u').write_text('#EXTM3U\n../secret.mp3\n')
            old=root/'STREAM_READY';old.mkdir();(old/'untouched.txt').write_text('KEEP')
            with self.assertRaises(ValueError):export_stream_ready(root,[block])
            self.assertEqual((old/'untouched.txt').read_text(),'KEEP')

@unittest.skipUnless(os.environ.get('AUTODJ_AUDIO_E2E')=='1','Set AUTODJ_AUDIO_E2E=1 to execute real synthetic audio processing')
class RealAudioSmoke(unittest.TestCase):
    def test_worker_mp3_cover_metadata_playlist_and_master(self):
        ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe')
        if not (ffmpeg and ffprobe):self.skipTest('FFmpeg and FFprobe unavailable')
        with tempfile.TemporaryDirectory() as d:
            tmp=Path(d);source=tmp/'signal.wav'; output=tmp/'out';output.mkdir()
            subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-f','lavfi','-i','sine=frequency=220:duration=0.75','-ac','2','-y',str(source)],check=True,timeout=30)
            # The existing bundled original covers are used unchanged.
            job={'files':[str(source)],'output':str(output),'profile':'stream','bitrate':256,
                 'block_mode':True,'split_mode':'TRACKS','target_tracks':1,'target_minutes':1,
                 'export_m3u':True,'write_metadata':True,'metadata_profile_path':str(ROOT/'legacy/metadata.json'),
                 'rotate_covers':True,'cover_dir':str(ROOT/'legacy/covers'), 'export_stream_ready':True}
            process=subprocess.run([sys.executable,str(ROOT/'engine/worker.py'),'--ffmpeg',ffmpeg,'--ffprobe',ffprobe],input=json.dumps(job),text=True,capture_output=True,timeout=120)
            self.assertEqual(process.returncode,0,process.stdout+'\n'+process.stderr)
            master=output/'STREAM_READY/master.m3u'
            self.assertTrue(master.is_file())
            self.assertEqual(master.read_text(encoding='utf-8-sig').strip().splitlines(),['#EXTM3U','BLOCK_001/signal.mp3'])
            audio=output/'STREAM_READY/BLOCK_001/signal.mp3'
            probe=subprocess.run([ffprobe,'-v','error','-show_entries','stream=codec_name,codec_type:format_tags=artist,title','-of','json',str(audio)],capture_output=True,text=True,check=True,timeout=30)
            info=json.loads(probe.stdout)
            self.assertIn('mp3',[s['codec_name'] for s in info['streams'] if s['codec_type']=='audio'])
            self.assertTrue(any(s['codec_type']=='video' for s in info['streams']),'Cover stream missing')
            self.assertTrue(info['format'].get('tags',{}).get('artist'),'Artist metadata missing')
            self.assertEqual(info['format'].get('tags',{}).get('title'),'signal')

if __name__=='__main__':unittest.main()
