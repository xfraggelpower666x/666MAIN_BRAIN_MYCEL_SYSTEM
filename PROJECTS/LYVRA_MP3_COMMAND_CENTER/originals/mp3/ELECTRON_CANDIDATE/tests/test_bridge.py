"""Real process integration of the Electron worker and original media_tools.py."""
import json, tempfile, unittest, subprocess, sys, pathlib, shutil, os, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
WORKER=ROOT/'engine_bridge.py'

def run(action):
    return subprocess.run([sys.executable,str(WORKER)],input=json.dumps(action)+'\n',capture_output=True,text=True,timeout=75)

class BridgeTest(unittest.TestCase):
    def test_check(self):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'): self.skipTest('ffmpeg not installed')
        p=run({'action':'check'});self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout.splitlines()[-1])['type'],'result')
    def test_reject_action(self):
        p=run({'action':'erase'});self.assertNotEqual(p.returncode,0);self.assertEqual(json.loads(p.stdout.splitlines()[-1])['type'],'error')
    def test_mp3_real_export_and_source_unchanged(self):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'): self.skipTest('ffmpeg not installed')
        with tempfile.TemporaryDirectory() as d:
            wav=pathlib.Path(d)/'reference.wav';mp3=pathlib.Path(d)/'out.mp3'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=800:duration=1','-c:a','pcm_s24le',str(wav)],check=True)
            pre=hashlib.sha256(wav.read_bytes()).hexdigest()
            p=run({'action':'export','source':str(wav),'destination':str(mp3),'stream':0,'images':[]})
            self.assertEqual(p.returncode,0,p.stderr+'\n'+p.stdout[-1500:]);self.assertTrue(mp3.exists())
            self.assertEqual(hashlib.sha256(wav.read_bytes()).hexdigest(),pre)
            self.assertEqual(json.loads(p.stdout.splitlines()[-1])['data']['status'],'TECHNICAL_DECODE_PASS')
            again=run({'action':'export','source':str(wav),'destination':str(mp3),'stream':0})
            self.assertNotEqual(again.returncode,0)
    def test_exclusive_publish_preserves_existing_bytes(self):
        sys.path.insert(0,str(ROOT))
        from engine_bridge import safe_publish
        with tempfile.TemporaryDirectory() as d:
            src=pathlib.Path(d)/"input";dst=pathlib.Path(d)/"existing"
            src.write_bytes(b"new data");dst.write_bytes(b"IMPORTANT_ORIGINAL")
            with self.assertRaises(FileExistsError):safe_publish(src,dst)
            self.assertEqual(dst.read_bytes(),b"IMPORTANT_ORIGINAL")
    def test_inspect(self):
        if not shutil.which('ffmpeg'):self.skipTest('ffmpeg missing')
        with tempfile.TemporaryDirectory() as d:
            wav=pathlib.Path(d)/'test (1).wav';subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=duration=1',str(wav)],check=True)
            p=run({'action':'inspect','source':str(wav)})
            self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout.splitlines()[-1])['data']['rename_preview'],'test 1.wav')
if __name__=='__main__':unittest.main()
