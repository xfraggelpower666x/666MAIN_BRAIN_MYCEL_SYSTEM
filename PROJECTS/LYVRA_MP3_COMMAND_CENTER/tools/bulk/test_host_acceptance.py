import hashlib, io, unittest
from host_acceptance import verify_bytes, provider_probe
DATA=b'\x00\xff\r\n\x00\x80ABC'
SHA=hashlib.sha1(b'blob '+str(len(DATA)).encode()+b'\0'+DATA).hexdigest()
SHA256=hashlib.sha256(DATA).hexdigest()
class Tests(unittest.TestCase):
    def test_bytes(self): self.assertEqual(verify_bytes(DATA,SHA,SHA256)['bytes'],len(DATA))
    def test_corruption(self):
        with self.assertRaises(ValueError): verify_bytes(DATA+b'x',SHA,SHA256)
    def test_sha256(self):
        with self.assertRaises(ValueError): verify_bytes(DATA,SHA,'0'*64)
    def test_provider_contract(self):
        def reader(req,timeout):
            self.assertTrue(req.full_url.endswith(SHA));return io.BytesIO(DATA)
        self.assertEqual(provider_probe(SHA,SHA256,reader)['sha'],SHA)
    def test_invalid(self):
        with self.assertRaises(ValueError):provider_probe('../bad',SHA256)
if __name__=='__main__':unittest.main()
