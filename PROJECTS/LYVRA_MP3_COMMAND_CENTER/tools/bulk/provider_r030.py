"""R03.0: unabhängiger GitHub-Blob-Readback synthetischer Binärbytes."""
import hashlib, json, os
from host_acceptance import provider_probe, verify_bytes
import urllib.request
from pathlib import Path
data=bytes([0,255,13,10,0,128,65,66,67])
sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
assert sha=='e3327c3bf0f98b4608437c1cb33189856a2ea9be'
receipt=provider_probe(sha,hashlib.sha256(data).hexdigest())
print(json.dumps({'gate':'provider_binary','commit':os.environ['GITHUB_SHA'],'status':'PASS',**receipt}))
