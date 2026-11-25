import runpy,subprocess,tempfile,pathlib,math,struct,wave
base=pathlib.Path(__file__).resolve().parents[1]
ns=runpy.run_path(str(base/'MP3_Manager.pyw'),run_name='qc_test_module')
fn=ns['verify_encoded_mp3']
with tempfile.TemporaryDirectory() as tmp:
    tmp=pathlib.Path(tmp)
    wav=tmp/'ORIGINAL.wav'; mp3=tmp/'OUTPUT.mp3'
    with wave.open(str(wav),'wb') as wf:
        wf.setnchannels(2);wf.setsampwidth(2);wf.setframerate(48000)
        frames=bytearray()
        for i in range(48000*2):
            v=int(18000*math.sin(2*math.pi*220*i/48000));frames+=struct.pack('<hh',v,v)
        wf.writeframes(frames)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),'-af','aformat=sample_fmts=fltp,aresample=48000','-ar','48000','-ac','2','-c:a','libmp3lame','-compression_level','0','-b:a','320k',str(mp3)]
    subprocess.run(cmd,check=True)
    ok=fn('ffmpeg','ffprobe',mp3,2.0)
    assert ok['decode']=='PASS',ok
    print('PASS: WAV -> 320k MP3 at 48k, decode all frames, duration '+str(ok['duration_seconds']))
    bad=tmp/'BROKEN.mp3';bad.write_bytes(b'not a real mp3 at all')
    try:fn('ffmpeg','ffprobe',bad,2.0)
    except RuntimeError as exc:print('PASS: invalid audio rejected:',str(exc)[:100])
    else:raise AssertionError('bad MP3 incorrectly accepted')
    try:fn('ffmpeg','ffprobe',mp3,12.0)
    except RuntimeError as exc:print('PASS: duration mismatch rejected')
    else:raise AssertionError('wrong source length accepted')
    assert 'self.normalize.set(mode==\'balanced\')' in (base/'MP3_Manager.pyw').read_text()
    assert "self.quality_preset.get() in ('maximum','original') and self.normalize.get()" in (base/'MP3_Manager.pyw').read_text()
    print('PASS: maximum/original normalize false preset + start guard')
